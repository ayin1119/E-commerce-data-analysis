import os
import joblib
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss
)


def resolve_path(base_file, relative_path):
    """
    接口定义：
        输入：当前文件路径、配置中的相对路径
        输出：绝对路径

    作用：
        使代码可以在项目目录中稳定读取输入文件和保存输出文件。
    """
    base_dir = os.path.dirname(os.path.abspath(base_file))
    return os.path.abspath(os.path.join(base_dir, relative_path))


def logit(probability):
    """
    接口定义：
        输入：概率数组
        输出：logit 转换后的数组

    作用：
        Platt Scaling 需要对原始概率做 logit 转换。
        为避免概率为 0 或 1 导致无穷值，先进行裁剪。
    """
    probability = np.clip(probability, 1e-6, 1 - 1e-6)
    return np.log(probability / (1 - probability))


def check_required_columns(df, config):
    """
    接口定义：
        输入：预测结果 DataFrame、配置字典
        输出：无

    作用：
        检查概率校准所需字段是否存在。
    """
    required_cols = [
        config["dataset_col"],
        config["target_col"],
        config["probability_col"]
    ]

    missing_cols = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:
        raise ValueError(
            "缺少必要字段："
            + "、".join(missing_cols)
            + "。请检查 XGBoost 预测结果文件。"
        )


def clean_prediction_data(df, config):
    """
    接口定义：
        输入：预测结果 DataFrame、配置字典
        输出：清洗后的 DataFrame

    作用：
        转换标签和概率字段，确保后续校准和指标计算稳定。
    """
    df = df.copy()
    target_col = config["target_col"]
    prob_col = config["probability_col"]

    df[target_col] = pd.to_numeric(
        df[target_col],
        errors="coerce"
    ).fillna(0).astype(int)

    df[prob_col] = pd.to_numeric(
        df[prob_col],
        errors="coerce"
    ).clip(1e-6, 1 - 1e-6)

    if df[prob_col].isna().any():
        raise ValueError("概率字段存在无法转换的缺失值，请检查输入文件。")

    return df


def split_valid_test(df, config):
    """
    接口定义：
        输入：清洗后的预测结果、配置字典
        输出：valid_df、test_df

    作用：
        valid 集用于拟合概率校准器，test 集用于评估校准效果。
    """
    dataset_col = config["dataset_col"]

    valid_df = df[df[dataset_col] == config["valid_value"]].copy()
    test_df = df[df[dataset_col] == config["test_value"]].copy()

    if valid_df.empty:
        raise ValueError("valid 数据集为空，无法拟合校准器。")

    if test_df.empty:
        raise ValueError("test 数据集为空，无法评估校准效果。")

    return valid_df, test_df


def fit_calibrators(valid_df, config):
    """
    接口定义：
        输入：valid 集预测结果、配置字典
        输出：Platt 校准器、Isotonic 校准器

    作用：
        使用 valid 集拟合概率校准器。
    """
    target_col = config["target_col"]
    prob_col = config["probability_col"]

    y_valid = valid_df[target_col].values
    valid_prob = valid_df[prob_col].values

    if len(np.unique(y_valid)) < 2:
        raise ValueError("valid 数据集中标签只有单一类别，无法拟合校准器。")

    # Platt Scaling：对 logit(probability) 再训练一个逻辑回归
    platt = LogisticRegression(solver="lbfgs", max_iter=1000)
    platt.fit(logit(valid_prob).reshape(-1, 1), y_valid)

    # Isotonic Regression：非参数单调校准
    isotonic = IsotonicRegression(out_of_bounds="clip")
    isotonic.fit(valid_prob, y_valid)

    return platt, isotonic


def add_calibrated_probabilities(df, config, platt, isotonic):
    """
    接口定义：
        输入：valid/test 预测结果、配置字典、两个校准器
        输出：带原始概率和校准后概率的 DataFrame

    作用：
        生成：
            original_xgb_probability
            platt_xgb_probability
            isotonic_xgb_probability
            calibrated_xgb_probability
    """
    out = df.copy()
    prob_col = config["probability_col"]
    original_prob = out[prob_col].values

    out["original_xgb_probability"] = original_prob

    out["platt_xgb_probability"] = platt.predict_proba(
        logit(original_prob).reshape(-1, 1)
    )[:, 1]

    out["isotonic_xgb_probability"] = isotonic.predict(original_prob)

    default_method = config.get("default_calibrated_method", "platt")

    if default_method == "platt":
        out["calibrated_xgb_probability"] = out["platt_xgb_probability"]
    elif default_method == "isotonic":
        out["calibrated_xgb_probability"] = out["isotonic_xgb_probability"]
    else:
        out["calibrated_xgb_probability"] = out["original_xgb_probability"]

    return out


def expected_calibration_error(y_true, prob, n_bins=10):
    """
    接口定义：
        输入：真实标签、预测概率、分箱数量
        输出：ECE、MCE、分箱明细表

    作用：
        衡量预测概率和真实购买率之间的偏差。
    """
    y_true = np.asarray(y_true)
    prob = np.asarray(prob)
    bins = np.linspace(0, 1, n_bins + 1)

    ece = 0.0
    mce = 0.0
    rows = []

    for i in range(n_bins):
        left = bins[i]
        right = bins[i + 1]

        if i == n_bins - 1:
            mask = (prob >= left) & (prob <= right)
        else:
            mask = (prob >= left) & (prob < right)

        count = int(mask.sum())

        if count == 0:
            rows.append({
                "bin": i + 1,
                "prob_left": left,
                "prob_right": right,
                "sample_count": 0,
                "mean_predicted_probability": np.nan,
                "actual_purchase_rate": np.nan,
                "absolute_gap": np.nan
            })
            continue

        mean_prob = float(prob[mask].mean())
        actual_rate = float(y_true[mask].mean())
        gap = abs(mean_prob - actual_rate)

        ece += (count / len(y_true)) * gap
        mce = max(mce, gap)

        rows.append({
            "bin": i + 1,
            "prob_left": left,
            "prob_right": right,
            "sample_count": count,
            "mean_predicted_probability": mean_prob,
            "actual_purchase_rate": actual_rate,
            "absolute_gap": gap
        })

    return ece, mce, pd.DataFrame(rows)


def evaluate_metrics(y_true, prob, split_name, method_name, n_bins):
    """
    接口定义：
        输入：真实标签、概率、数据集名称、方法名称、分箱数量
        输出：一行指标字典、分箱报告 DataFrame

    作用：
        同时计算排序指标和概率校准指标。
    """
    y_true = np.asarray(y_true)
    prob_clip = np.clip(np.asarray(prob), 1e-6, 1 - 1e-6)

    if len(np.unique(y_true)) < 2:
        auc = np.nan
        pr_auc = np.nan
    else:
        auc = roc_auc_score(y_true, prob_clip)
        pr_auc = average_precision_score(y_true, prob_clip)

    ece, mce, bin_df = expected_calibration_error(
        y_true,
        prob_clip,
        n_bins=n_bins
    )

    metrics = {
        "split": split_name,
        "method": method_name,
        "sample_count": len(y_true),
        "positive_count": int(y_true.sum()),
        "positive_rate": round(float(np.mean(y_true)), 6),
        "auc": round(float(auc), 6) if not np.isnan(auc) else np.nan,
        "pr_auc": round(float(pr_auc), 6) if not np.isnan(pr_auc) else np.nan,
        "brier_score": round(float(brier_score_loss(y_true, prob_clip)), 6),
        "log_loss": round(float(log_loss(y_true, prob_clip, labels=[0, 1])), 6),
        f"ece_{n_bins}bins": round(float(ece), 6),
        f"mce_{n_bins}bins": round(float(mce), 6),
        "mean_predicted_probability": round(float(np.mean(prob_clip)), 6)
    }

    bin_df.insert(0, "method", method_name)
    bin_df.insert(0, "split", split_name)

    return metrics, bin_df


def evaluate_top_rates(df, target_col, prob_col, method_name, split_name, top_rates):
    """
    接口定义：
        输入：数据集、标签字段、概率字段、方法名称、数据集名称、Top比例
        输出：Top比例评估结果列表

    作用：
        检查校准后是否破坏排序能力。
    """
    y_true = df[target_col].reset_index(drop=True)
    prob = df[prob_col].reset_index(drop=True)
    total_positive = y_true.sum()

    rows = []

    for rate in top_rates:
        top_n = max(1, int(len(df) * rate))
        top_idx = prob.nlargest(top_n).index
        top_y = y_true.loc[top_idx]

        rows.append({
            "split": split_name,
            "method": method_name,
            "top_rate": rate,
            "top_n": top_n,
            "top_precision": round(float(top_y.mean()), 6),
            "top_recall": round(float(top_y.sum() / total_positive), 6)
            if total_positive > 0 else 0
        })

    return rows


def run_xgb_calibration(config):
    """
    统一接口定义：
        输入：
            config：XGBoost 概率校准配置字典

        输出：
            outputs：校准预测结果、指标、分箱报告、Top指标和校准器路径

    作用：
        完成：
            读取 XGBoost 预测结果
            → 检查字段
            → 清洗概率
            → valid/test 划分
            → 拟合 Platt 和 Isotonic 校准器
            → 生成校准概率
            → 计算校准指标
            → 保存结果文件。
    """
    prediction_path = resolve_path(__file__, config["prediction_path"])
    output_dir = resolve_path(__file__, config["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    print("读取 XGBoost 预测结果：", prediction_path)
    pred = pd.read_csv(prediction_path)

    check_required_columns(pred, config)
    pred = clean_prediction_data(pred, config)

    valid_df, test_df = split_valid_test(pred, config)

    platt, isotonic = fit_calibrators(valid_df, config)

    valid_out = add_calibrated_probabilities(
        valid_df,
        config,
        platt,
        isotonic
    )

    test_out = add_calibrated_probabilities(
        test_df,
        config,
        platt,
        isotonic
    )

    calibrated_pred = pd.concat(
        [valid_out, test_out],
        ignore_index=True
    )

    methods = {
        "original": "original_xgb_probability",
        "platt": "platt_xgb_probability",
        "isotonic": "isotonic_xgb_probability",
        "calibrated": "calibrated_xgb_probability"
    }

    metric_rows = []
    bin_parts = []
    top_rows = []

    for split_name, df_part in [
        (config["valid_value"], valid_out),
        (config["test_value"], test_out)
    ]:
        y_true = df_part[config["target_col"]].values

        for method_name, probability_column in methods.items():
            prob = df_part[probability_column].values

            metrics, bin_df = evaluate_metrics(
                y_true=y_true,
                prob=prob,
                split_name=split_name,
                method_name=method_name,
                n_bins=config["n_bins"]
            )

            metric_rows.append(metrics)
            bin_parts.append(bin_df)

            top_rows.extend(
                evaluate_top_rates(
                    df=df_part,
                    target_col=config["target_col"],
                    prob_col=probability_column,
                    method_name=method_name,
                    split_name=split_name,
                    top_rates=config["top_rates"]
                )
            )

    metrics_df = pd.DataFrame(metric_rows)
    bin_report = pd.concat(bin_parts, ignore_index=True)
    top_df = pd.DataFrame(top_rows)

    calibrated_prediction_path = os.path.join(
        output_dir,
        config["calibrated_prediction_filename"]
    )
    metrics_path = os.path.join(
        output_dir,
        config["calibration_metrics_filename"]
    )
    bin_path = os.path.join(
        output_dir,
        config["calibration_bin_report_filename"]
    )
    top_path = os.path.join(
        output_dir,
        config["calibration_top_rate_filename"]
    )
    calibrator_path = os.path.join(
        output_dir,
        config["calibrator_filename"]
    )

    calibrated_pred.to_csv(
        calibrated_prediction_path,
        index=False,
        encoding="utf-8-sig"
    )
    metrics_df.to_csv(
        metrics_path,
        index=False,
        encoding="utf-8-sig"
    )
    bin_report.to_csv(
        bin_path,
        index=False,
        encoding="utf-8-sig"
    )
    top_df.to_csv(
        top_path,
        index=False,
        encoding="utf-8-sig"
    )

    joblib.dump(
        {
            "platt": platt,
            "isotonic": isotonic,
            "input_probability_col": config["probability_col"],
            "default_calibrated_method": config.get("default_calibrated_method", "platt"),
            "output_probability_col": "calibrated_xgb_probability",
            "target_col": config["target_col"],
            "fit_split": config["valid_value"],
            "n_bins": config["n_bins"]
        },
        calibrator_path
    )

    return {
        "calibrated_prediction_path": calibrated_prediction_path,
        "metrics_path": metrics_path,
        "bin_path": bin_path,
        "top_path": top_path,
        "calibrator_path": calibrator_path
    }
