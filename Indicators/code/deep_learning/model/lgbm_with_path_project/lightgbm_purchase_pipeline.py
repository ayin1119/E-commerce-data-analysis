import os
import time
import joblib
import numpy as np
import pandas as pd
import lightgbm as lgb

from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    brier_score_loss,
    log_loss
)


def resolve_path(base_file, relative_path):
    base_dir = os.path.dirname(os.path.abspath(base_file))
    return os.path.abspath(os.path.join(base_dir, relative_path))


def make_xy(df, features, target_col):
    X = df[features].apply(pd.to_numeric, errors="coerce")
    y = df[target_col].astype("int8")
    return X, y


def prepare_data(train_df, valid_df, test_df, features, target_col):
    X_train_raw, y_train = make_xy(train_df, features, target_col)
    X_valid_raw, y_valid = make_xy(valid_df, features, target_col)
    X_test_raw, y_test = make_xy(test_df, features, target_col)

    imputer = SimpleImputer(strategy="median")
    X_train = imputer.fit_transform(X_train_raw).astype("float32")
    X_valid = imputer.transform(X_valid_raw).astype("float32")
    X_test = imputer.transform(X_test_raw).astype("float32")

    return X_train, y_train.values, X_valid, y_valid.values, X_test, y_test.values, imputer


def build_model(config, scale_pos_weight=None):
    params = {
        "objective": "binary",
        "boosting_type": "gbdt",
        "n_estimators": config["n_estimators"],
        "learning_rate": config["learning_rate"],
        "num_leaves": config["num_leaves"],
        "max_depth": config["max_depth"],
        "min_child_samples": config["min_child_samples"],
        "subsample": config["subsample"],
        "subsample_freq": config["subsample_freq"],
        "colsample_bytree": config["colsample_bytree"],
        "reg_alpha": config["reg_alpha"],
        "reg_lambda": config["reg_lambda"],
        "max_bin": config["max_bin"],
        "random_state": config["random_state"],
        "n_jobs": config["n_jobs"],
        "verbosity": -1,
        "force_col_wise": True
    }

    if scale_pos_weight is not None:
        params["scale_pos_weight"] = scale_pos_weight

    return lgb.LGBMClassifier(**params)


def evaluate_metrics(y_true, prob, split, experiment, feature_count, train_time):
    prob_clip = np.clip(prob, 1e-6, 1 - 1e-6)

    return {
        "experiment": experiment,
        "feature_count": feature_count,
        "split": split,
        "sample_count": len(y_true),
        "positive_count": int(np.sum(y_true)),
        "positive_rate": round(float(np.mean(y_true)), 6),
        "auc": round(float(roc_auc_score(y_true, prob)), 6),
        "pr_auc": round(float(average_precision_score(y_true, prob)), 6),
        "brier_score": round(float(brier_score_loss(y_true, prob_clip)), 6),
        "log_loss": round(float(log_loss(y_true, prob_clip, labels=[0, 1])), 6),
        "train_time_seconds": round(float(train_time), 4)
    }


def evaluate_top_rates(y_true, prob, split, experiment, feature_count, top_rates):
    y_true = pd.Series(y_true).reset_index(drop=True)
    prob = pd.Series(prob).reset_index(drop=True)
    total_positive = y_true.sum()

    rows = []

    for rate in top_rates:
        top_n = max(1, int(len(y_true) * rate))
        top_index = prob.nlargest(top_n).index
        top_y = y_true.loc[top_index]

        rows.append({
            "experiment": experiment,
            "feature_count": feature_count,
            "split": split,
            "top_rate": rate,
            "top_n": top_n,
            "top_precision": round(float(top_y.mean()), 6),
            "top_recall": round(float(top_y.sum() / total_positive), 6)
            if total_positive > 0 else 0
        })

    return rows


def run_lgbm_experiment(config):
    data_path = resolve_path(__file__, config["data_path"])
    feature_path = resolve_path(__file__, config["selected_feature_path"])
    output_dir = resolve_path(__file__, config["output_dir"])
    os.makedirs(output_dir, exist_ok=True)

    print("读取宽表：", data_path)
    df = pd.read_csv(data_path)

    print("读取特征列表：", feature_path)
    feature_list_df = pd.read_csv(feature_path)

    target_col = config["target_col"]
    dataset_col = config["dataset_col"]
    drop_columns = set(config["drop_columns"])

    df[target_col] = pd.to_numeric(
        df[target_col],
        errors="coerce"
    ).fillna(0).astype("int8")

    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    all_features = [c for c in numeric_columns if c not in drop_columns]

    top20_features = (
        feature_list_df[feature_list_df["experiment"] == "top20_features"]
        .sort_values("feature_rank")["feature"]
        .tolist()
    )
    top20_features = [f for f in top20_features if f in all_features]

    train_df = df[df[dataset_col] == config["train_value"]].copy()
    valid_df = df[df[dataset_col] == config["valid_value"]].copy()
    test_df = df[df[dataset_col] == config["test_value"]].copy()

    train_pos = int(train_df[target_col].sum())
    train_neg = int(len(train_df) - train_pos)
    scale_pos_weight = train_neg / train_pos

    feature_sets = {}
    if "top20" in config["run_feature_sets"]:
        feature_sets["lgbm_top20"] = top20_features
    if "all_features" in config["run_feature_sets"]:
        feature_sets["lgbm_all_features"] = all_features

    experiments = []
    for name, features in feature_sets.items():
        if "no_weight" in config["run_weight_options"]:
            experiments.append((f"{name}_no_weight", features, None))
        if "scale_pos_weight" in config["run_weight_options"]:
            experiments.append((f"{name}_scale_pos_weight", features, scale_pos_weight))

    metric_rows = []
    top_rows = []
    importance_parts = []
    model_dict = {}
    imputer_dict = {}
    feature_dict = {}
    pred_dict = {}

    for exp_name, features, weight in experiments:
        print("开始训练：", exp_name, "特征数：", len(features))

        X_train, y_train, X_valid, y_valid, X_test, y_test, imputer = prepare_data(
            train_df,
            valid_df,
            test_df,
            features,
            target_col
        )

        model = build_model(config, scale_pos_weight=weight)

        start = time.perf_counter()
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_valid, y_valid)],
            eval_metric="auc",
            callbacks=[lgb.log_evaluation(period=0)]
        )
        train_time = time.perf_counter() - start

        valid_prob = model.predict_proba(X_valid)[:, 1]
        test_prob = model.predict_proba(X_test)[:, 1]

        metric_rows.append(
            evaluate_metrics(
                y_valid,
                valid_prob,
                config["valid_value"],
                exp_name,
                len(features),
                train_time
            )
        )
        metric_rows.append(
            evaluate_metrics(
                y_test,
                test_prob,
                config["test_value"],
                exp_name,
                len(features),
                train_time
            )
        )

        top_rows.extend(
            evaluate_top_rates(
                y_valid,
                valid_prob,
                config["valid_value"],
                exp_name,
                len(features),
                config["top_rates"]
            )
        )
        top_rows.extend(
            evaluate_top_rates(
                y_test,
                test_prob,
                config["test_value"],
                exp_name,
                len(features),
                config["top_rates"]
            )
        )

        booster = model.booster_
        imp = pd.DataFrame({
            "experiment": exp_name,
            "feature": features,
            "importance_gain": booster.feature_importance(importance_type="gain"),
            "importance_split": booster.feature_importance(importance_type="split")
        }).sort_values("importance_gain", ascending=False).reset_index(drop=True)
        imp["rank_gain"] = np.arange(1, len(imp) + 1)
        importance_parts.append(imp)

        model_dict[exp_name] = model
        imputer_dict[exp_name] = imputer
        feature_dict[exp_name] = features
        pred_dict[exp_name] = {
            "valid_prob": valid_prob,
            "test_prob": test_prob
        }

    metrics_df = pd.DataFrame(metric_rows)
    top_df = pd.DataFrame(top_rows)
    importance_df = pd.concat(importance_parts, ignore_index=True)

    summary_rows = []
    for exp in metrics_df["experiment"].unique():
        valid_m = metrics_df[
            (metrics_df["experiment"] == exp) &
            (metrics_df["split"] == config["valid_value"])
        ].iloc[0]

        test_m = metrics_df[
            (metrics_df["experiment"] == exp) &
            (metrics_df["split"] == config["test_value"])
        ].iloc[0]

        test_top10 = top_df[
            (top_df["experiment"] == exp) &
            (top_df["split"] == config["test_value"]) &
            (top_df["top_rate"] == 0.10)
        ].iloc[0]

        summary_rows.append({
            "model_type": "LightGBM",
            "experiment": exp,
            "feature_count": int(test_m["feature_count"]),
            "valid_auc": valid_m["auc"],
            "valid_pr_auc": valid_m["pr_auc"],
            "test_auc": test_m["auc"],
            "test_pr_auc": test_m["pr_auc"],
            "test_top10_precision": test_top10["top_precision"],
            "test_top10_recall": test_top10["top_recall"],
            "train_time_seconds": test_m["train_time_seconds"]
        })

    summary_df = pd.DataFrame(summary_rows)
    best_exp = summary_df.sort_values(
        by=["valid_pr_auc", "valid_auc", "test_pr_auc"],
        ascending=False
    ).iloc[0]["experiment"]

    best_model = model_dict[best_exp]
    best_imputer = imputer_dict[best_exp]
    best_features = feature_dict[best_exp]

    valid_result = valid_df[config["id_columns"]].copy()
    valid_result["lgbm_probability"] = pred_dict[best_exp]["valid_prob"]

    test_result = test_df[config["id_columns"]].copy()
    test_result["lgbm_probability"] = pred_dict[best_exp]["test_prob"]

    prediction_result = pd.concat(
        [valid_result, test_result],
        ignore_index=True
    )

    summary_path = os.path.join(output_dir, "lgbm_experiment_summary_with_path.csv")
    metrics_path = os.path.join(output_dir, "lgbm_model_metrics_with_path.csv")
    top_path = os.path.join(output_dir, "lgbm_top_rate_metrics_with_path.csv")
    importance_path = os.path.join(output_dir, "lgbm_feature_importance_with_path.csv")
    pred_path = os.path.join(output_dir, "lgbm_predictions_best_with_path.csv")
    model_path = os.path.join(output_dir, f"best_lgbm_model_{best_exp}.joblib")
    features_path = os.path.join(output_dir, f"best_lgbm_features_{best_exp}.csv")

    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    metrics_df.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    top_df.to_csv(top_path, index=False, encoding="utf-8-sig")
    importance_df.to_csv(importance_path, index=False, encoding="utf-8-sig")
    prediction_result.to_csv(pred_path, index=False, encoding="utf-8-sig")
    pd.DataFrame({"feature": best_features}).to_csv(
        features_path,
        index=False,
        encoding="utf-8-sig"
    )

    joblib.dump(
        {
            "model": best_model,
            "imputer": best_imputer,
            "features": best_features,
            "experiment": best_exp,
            "target_col": target_col,
            "id_columns": config["id_columns"]
        },
        model_path
    )

    return {
        "summary_path": summary_path,
        "metrics_path": metrics_path,
        "top_path": top_path,
        "importance_path": importance_path,
        "prediction_path": pred_path,
        "model_path": model_path,
        "features_path": features_path,
        "best_experiment": best_exp
    }
