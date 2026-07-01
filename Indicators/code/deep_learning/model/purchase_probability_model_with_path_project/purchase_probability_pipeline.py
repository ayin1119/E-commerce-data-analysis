from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import os

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score, average_precision_score


def load_data(config):
    # 获取当前文件所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 拼接完整路径
    data_path = os.path.join(base_dir, config["data_path"])
    data_path = os.path.abspath(data_path)  # 转为绝对路径
    
    print(f"读取文件: {data_path}")
    df = pd.read_csv(data_path)
    return df


def check_required_columns(df, config):
    """
    接口定义：
    输入：DataFrame、config 配置字典
    输出：无

    作用：
    检查必要字段是否存在。
    """
    required_columns = [
        config["dataset_col"],
        config["target_col"]
    ]

    # 如果配置文件中写了必须存在的新增特征，也一起检查
    # 这次用于确认行为路径特征是否已经成功进入宽表
    required_columns.extend(
        config.get("required_feature_columns", [])
    )

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "缺少必要字段："
            + "、".join(missing_columns)
            + "。请检查输入宽表字段是否正确。"
        )


def get_feature_columns(df, config):
    """
    接口定义：
    输入：DataFrame、config 配置字典
    输出：特征列列表

    作用：
    自动选择数值型特征，并排除 ID、日期、标签等字段。
    """
    drop_columns = set(config["drop_columns"])

    numeric_columns = df.select_dtypes(
        include=[np.number]
    ).columns.tolist()

    feature_columns = [
        col for col in numeric_columns
        if col not in drop_columns
    ]

    if not feature_columns:
        raise ValueError("没有找到可用于训练的数值型特征，请检查宽表字段。")

    required_features = config.get("required_feature_columns", [])
    used_required_features = [
        col for col in required_features
        if col in feature_columns
    ]

    print("模型特征数量：", len(feature_columns))
    print("新增行为路径特征进入模型：", used_required_features)

    return feature_columns


def optimize_memory(df, feature_columns, config):
    """
    接口定义：
    输入：DataFrame、特征列列表、config 配置字典
    输出：优化后的 DataFrame

    作用：
    将模型特征转成 float32，减少内存占用。
    """
    df = df.copy()

    target_col = config["target_col"]

    for col in feature_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

        if config.get("use_float32", True):
            df[col] = df[col].astype("float32")

    df[target_col] = pd.to_numeric(
        df[target_col],
        errors="coerce"
    ).fillna(0).astype("int8")

    return df


def split_dataset(df, config):
    """
    接口定义：
    输入：DataFrame、config 配置字典
    输出：训练集、验证集、测试集

    作用：
    根据 dataset_type 划分 train、valid、test。
    """
    dataset_col = config["dataset_col"]

    train_df = df[df[dataset_col] == config["train_value"]].copy()
    valid_df = df[df[dataset_col] == config["valid_value"]].copy()
    test_df = df[df[dataset_col] == config["test_value"]].copy()

    if train_df.empty:
        raise ValueError("训练集为空，请检查 dataset_type 是否包含 train。")

    if valid_df.empty:
        raise ValueError("验证集为空，请检查 dataset_type 是否包含 valid。")

    if test_df.empty:
        raise ValueError("测试集为空，请检查 dataset_type 是否包含 test。")

    return train_df, valid_df, test_df


def make_xy(data_df, feature_columns, config):
    """
    接口定义：
    输入：数据集、特征列、config 配置字典
    输出：X 特征矩阵、y 标签

    作用：
    从数据集中拆出模型输入 X 和目标 y。
    """
    target_col = config["target_col"]

    X = data_df[feature_columns]
    y = data_df[target_col].astype("int8")

    return X, y


def build_model(config):
    """
    接口定义：
    输入：config 配置字典
    输出：sklearn Pipeline 模型

    作用：
    构建购买概率模型。

    优化点：
    使用 SGDClassifier(loss='log_loss') 训练逻辑回归。
    它每轮只需要线性扫描数据，适合较大的特征宽表。
    """
    model = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", SGDClassifier(
            loss="log_loss",
            class_weight=config.get("class_weight", "balanced"),
            max_iter=config["max_iter"],
            tol=config["tol"],
            random_state=config["random_state"],
            n_jobs=-1
        ))
    ])

    return model


def train_model(model, X_train, y_train):
    """
    接口定义：
    输入：模型、训练特征、训练标签
    输出：训练后的模型

    作用：
    训练购买概率模型。
    """
    model.fit(X_train, y_train)
    return model


def predict_probability(model, X):
    """
    接口定义：
    输入：模型、特征矩阵
    输出：购买概率数组

    作用：
    预测未来 7 天购买概率。
    """
    return model.predict_proba(X)[:, 1]


def evaluate_auc_metrics(y_true, pred_prob, split_name):
    """
    接口定义：
    输入：真实标签、预测概率、数据集名称
    输出：一行指标字典

    作用：
    计算 AUC 和 PR-AUC。
    """
    y_true = pd.Series(y_true)

    if y_true.nunique() < 2:
        auc = np.nan
        pr_auc = np.nan
    else:
        auc = roc_auc_score(y_true, pred_prob)
        pr_auc = average_precision_score(y_true, pred_prob)

    return {
        "split": split_name,
        "sample_count": len(y_true),
        "positive_count": int(y_true.sum()),
        "positive_rate": round(float(y_true.mean()), 6),
        "auc": round(float(auc), 6) if not np.isnan(auc) else np.nan,
        "pr_auc": round(float(pr_auc), 6) if not np.isnan(pr_auc) else np.nan
    }


def evaluate_top_rates(y_true, pred_prob, split_name, top_rates):
    """
    接口定义：
    输入：真实标签、预测概率、数据集名称、Top 比例列表
    输出：Top 比例评估结果 DataFrame

    作用：
    评估模型认为最可能购买的前 5%、10%、20% 样本中，
    真实购买率有多高。

    时间复杂度优化：
    使用 nlargest 直接取 TopK，不对全量预测结果完整排序。
    """
    y_true = pd.Series(y_true).reset_index(drop=True)
    prob = pd.Series(pred_prob)

    rows = []

    total_positive = y_true.sum()

    for rate in top_rates:
        top_n = max(1, int(len(y_true) * rate))

        # nlargest 是 TopK 思路，不需要完整排序
        top_index = prob.nlargest(top_n).index
        top_y = y_true.loc[top_index]

        precision = top_y.mean()
        recall = top_y.sum() / total_positive if total_positive > 0 else 0

        rows.append({
            "split": split_name,
            "top_rate": rate,
            "top_n": top_n,
            "top_precision": round(float(precision), 6),
            "top_recall": round(float(recall), 6)
        })

    return pd.DataFrame(rows)


def build_prediction_result(data_df, pred_prob, config):
    """
    接口定义：
    输入：原始数据集、预测概率、config 配置字典
    输出：预测结果表

    作用：
    保存 user_id、item_id、真实标签和预测购买概率。
    """
    keep_cols = [
        col for col in config["id_columns"]
        if col in data_df.columns
    ]

    result = data_df[keep_cols].copy()
    result["buy_probability"] = pred_prob

    return result


def get_feature_importance(model, feature_columns, config):
    """
    接口定义：
    输入：模型、特征列、config 配置字典
    输出：特征重要性表

    作用：
    提取逻辑回归系数，查看哪些特征对购买概率影响较大。

    说明：
    这里使用 abs(coef) 衡量影响强度。
    """
    clf = model.named_steps["clf"]
    coef = clf.coef_[0]

    importance = pd.DataFrame({
        "feature": feature_columns,
        "coef": coef,
        "abs_coef": np.abs(coef)
    })

    top_n = config.get("top_n_features", 50)

    # 使用 nlargest 取 TopN，避免完整排序
    importance = importance.nlargest(
        top_n,
        "abs_coef"
    ).reset_index(drop=True)

    return importance


def save_outputs(model, metrics_df, top_rate_df, feature_importance,
                 prediction_result, config):
    """
    接口定义：
    输入：模型、各类结果表、config 配置字典
    输出：保存路径字典

    作用：
    保存模型、评估指标、Top 比例评估、特征重要性和预测结果。
    """
    # 获取当前文件所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 拼接输出目录（相对路径转绝对路径）
    output_dir = os.path.join(base_dir, config["output_dir"])
    output_dir = os.path.abspath(output_dir)
    
    # 创建输出目录（如果不存在）
    os.makedirs(output_dir, exist_ok=True)
    
    print(f" 输出目录: {output_dir}")

    model_path = os.path.join(output_dir, config["model_filename"])
    metrics_path = os.path.join(output_dir, config["metrics_filename"])
    top_rate_path = os.path.join(output_dir, config["top_rate_metrics_filename"])
    feature_importance_path = os.path.join(output_dir, config["feature_importance_filename"])
    prediction_path = os.path.join(output_dir, config["prediction_filename"])

    joblib.dump(model, model_path)

    metrics_df.to_csv(
        metrics_path,
        index=False,
        encoding="utf-8-sig"
    )

    top_rate_df.to_csv(
        top_rate_path,
        index=False,
        encoding="utf-8-sig"
    )

    feature_importance.to_csv(
        feature_importance_path,
        index=False,
        encoding="utf-8-sig"
    )

    prediction_result.to_csv(
        prediction_path,
        index=False,
        encoding="utf-8-sig"
    )

    return {
        "model_path": model_path,
        "metrics_path": metrics_path,
        "top_rate_path": top_rate_path,
        "feature_importance_path": feature_importance_path,
        "prediction_path": prediction_path
    }


def run_purchase_probability_model(config):
    """
    统一接口定义：
    输入：
        config：配置参数字典

    输出：
        outputs：包含模型、指标、预测结果路径的字典

    作用：
        外部只需要调用这个函数，就能完成：
        读取数据 → 选择特征 → 训练模型 → 预测概率 → 评估 → 保存结果。
    """
    df = load_data(config)
    check_required_columns(df, config)

    feature_columns = get_feature_columns(df, config)
    df = optimize_memory(df, feature_columns, config)

    train_df, valid_df, test_df = split_dataset(df, config)

    X_train, y_train = make_xy(train_df, feature_columns, config)
    X_valid, y_valid = make_xy(valid_df, feature_columns, config)
    X_test, y_test = make_xy(test_df, feature_columns, config)

    model = build_model(config)
    model = train_model(model, X_train, y_train)

    valid_prob = predict_probability(model, X_valid)
    test_prob = predict_probability(model, X_test)

    metrics_df = pd.DataFrame([
        evaluate_auc_metrics(y_valid, valid_prob, "valid"),
        evaluate_auc_metrics(y_test, test_prob, "test")
    ])

    top_rate_df = pd.concat([
        evaluate_top_rates(
            y_valid,
            valid_prob,
            "valid",
            config["top_rates"]
        ),
        evaluate_top_rates(
            y_test,
            test_prob,
            "test",
            config["top_rates"]
        )
    ], ignore_index=True)

    valid_prediction = build_prediction_result(
        valid_df,
        valid_prob,
        config
    )

    test_prediction = build_prediction_result(
        test_df,
        test_prob,
        config
    )

    prediction_result = pd.concat(
        [valid_prediction, test_prediction],
        ignore_index=True
    )

    feature_importance = get_feature_importance(
        model,
        feature_columns,
        config
    )

    outputs = save_outputs(
        model,
        metrics_df,
        top_rate_df,
        feature_importance,
        prediction_result,
        config
    )

    outputs["feature_count"] = len(feature_columns)
    outputs["train_shape"] = X_train.shape
    outputs["valid_shape"] = X_valid.shape
    outputs["test_shape"] = X_test.shape

    return outputs
