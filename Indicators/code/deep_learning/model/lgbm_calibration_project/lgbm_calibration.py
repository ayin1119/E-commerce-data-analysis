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
    base_dir = os.path.dirname(os.path.abspath(base_file))
    return os.path.abspath(os.path.join(base_dir, relative_path))


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def expected_calibration_error(y_true, prob, n_bins=10):
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


def evaluate_top_rates(df, target_col, prob_col, method_name, split_name, top_rates):
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


def run_lgbm_calibration(config):
    prediction_path = resolve_path(__file__, config["prediction_path"])
    output_dir = resolve_path(__file__, config["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    print("读取 LightGBM 预测结果：", prediction_path)
    pred = pd.read_csv(prediction_path)

    dataset_col = config["dataset_col"]
    target_col = config["target_col"]
    prob_col = config["probability_col"]

    required_cols = [dataset_col, target_col, prob_col]
    missing_cols = [col for col in required_cols if col not in pred.columns]

    if missing_cols:
        raise ValueError("缺少必要字段：" + "、".join(missing_cols))

    pred = pred.copy()
    pred[target_col] = pd.to_numeric(
        pred[target_col],
        errors="coerce"
    ).fillna(0).astype(int)

    pred[prob_col] = pd.to_numeric(
        pred[prob_col],
        errors="coerce"
    ).clip(1e-6, 1 - 1e-6)

    valid_df = pred[pred[dataset_col] == config["valid_value"]].copy()
    test_df = pred[pred[dataset_col] == config["test_value"]].copy()

    if valid_df.empty:
        raise ValueError("valid 数据集为空，无法拟合校准器。")

    if test_df.empty:
        raise ValueError("test 数据集为空，无法评估校准效果。")

    y_valid = valid_df[target_col].values
    valid_prob = valid_df[prob_col].values

    platt = LogisticRegression(solver="lbfgs", max_iter=1000)
    platt.fit(logit(valid_prob).reshape(-1, 1), y_valid)

    isotonic = IsotonicRegression(out_of_bounds="clip")
    isotonic.fit(valid_prob, y_valid)

    def add_probs(df):
        out = df.copy()
        original_prob = out[prob_col].values
        out["original_lgbm_probability"] = original_prob
        out["platt_lgbm_probability"] = platt.predict_proba(
            logit(original_prob).reshape(-1, 1)
        )[:, 1]
        out["isotonic_lgbm_probability"] = isotonic.predict(original_prob)
        return out

    valid_out = add_probs(valid_df)
    test_out = add_probs(test_df)

    calibrated_pred = pd.concat(
        [valid_out, test_out],
        ignore_index=True
    )

    methods = {
        "original": "original_lgbm_probability",
        "platt": "platt_lgbm_probability",
        "isotonic": "isotonic_lgbm_probability"
    }

    metric_rows = []
    bin_parts = []
    top_rows = []

    for split_name, df_part in [
        (config["valid_value"], valid_out),
        (config["test_value"], test_out)
    ]:
        y_true = df_part[target_col].values

        for method_name, prob_col_name in methods.items():
            prob = df_part[prob_col_name].values
            prob_clip = np.clip(prob, 1e-6, 1 - 1e-6)

            ece, mce, bin_df = expected_calibration_error(
                y_true,
                prob_clip,
                n_bins=config["n_bins"]
            )

            metric_rows.append({
                "split": split_name,
                "method": method_name,
                "sample_count": len(df_part),
                "positive_count": int(y_true.sum()),
                "positive_rate": round(float(np.mean(y_true)), 6),
                "auc": round(float(roc_auc_score(y_true, prob_clip)), 6),
                "pr_auc": round(float(average_precision_score(y_true, prob_clip)), 6),
                "brier_score": round(float(brier_score_loss(y_true, prob_clip)), 6),
                "log_loss": round(float(log_loss(y_true, prob_clip, labels=[0, 1])), 6),
                "ece_10bins": round(float(ece), 6),
                "mce_10bins": round(float(mce), 6),
                "mean_predicted_probability": round(float(np.mean(prob_clip)), 6)
            })

            bin_df.insert(0, "method", method_name)
            bin_df.insert(0, "split", split_name)
            bin_parts.append(bin_df)

            top_rows.extend(
                evaluate_top_rates(
                    df=df_part,
                    target_col=target_col,
                    prob_col=prob_col_name,
                    method_name=method_name,
                    split_name=split_name,
                    top_rates=config["top_rates"]
                )
            )

    metrics_df = pd.DataFrame(metric_rows)
    bin_report = pd.concat(bin_parts, ignore_index=True)
    top_df = pd.DataFrame(top_rows)

    cal_pred_path = os.path.join(
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

    calibrated_pred.to_csv(cal_pred_path, index=False, encoding="utf-8-sig")
    metrics_df.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    bin_report.to_csv(bin_path, index=False, encoding="utf-8-sig")
    top_df.to_csv(top_path, index=False, encoding="utf-8-sig")

    joblib.dump(
        {
            "platt": platt,
            "isotonic": isotonic,
            "input_probability_col": config["probability_col"],
            "target_col": target_col,
            "fit_split": config["valid_value"]
        },
        calibrator_path
    )

    return {
        "calibrated_prediction_path": cal_pred_path,
        "metrics_path": metrics_path,
        "bin_path": bin_path,
        "top_path": top_path,
        "calibrator_path": calibrator_path
    }
