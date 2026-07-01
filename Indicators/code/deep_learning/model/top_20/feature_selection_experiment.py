from pathlib import Path
import os
import time
import joblib
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import roc_auc_score, average_precision_score


def resolve_path(base_file, relative_path):
    base_dir = os.path.dirname(os.path.abspath(base_file))
    return os.path.abspath(os.path.join(base_dir, relative_path))


def build_model(config):
    return Pipeline([
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


def make_xy(df, features, target_col):
    X = df[features].apply(pd.to_numeric, errors="coerce").astype("float32")
    y = df[target_col].astype("int8")
    return X, y


def evaluate_auc_pr(y_true, prob, split, experiment, feature_count, train_time):
    return {
        "experiment": experiment,
        "feature_count": feature_count,
        "split": split,
        "sample_count": len(y_true),
        "positive_count": int(np.sum(y_true)),
        "positive_rate": round(float(np.mean(y_true)), 6),
        "auc": round(float(roc_auc_score(y_true, prob)), 6),
        "pr_auc": round(float(average_precision_score(y_true, prob)), 6),
        "train_time_seconds": round(float(train_time), 4)
    }


def evaluate_top_rates(y_true, prob, split, experiment, feature_count, top_rates):
    y_true = pd.Series(y_true).reset_index(drop=True)
    prob = pd.Series(prob).reset_index(drop=True)
    total_pos = y_true.sum()

    rows = []

    for rate in top_rates:
        top_n = max(1, int(len(y_true) * rate))
        idx = prob.nlargest(top_n).index
        top_y = y_true.loc[idx]

        rows.append({
            "experiment": experiment,
            "feature_count": feature_count,
            "split": split,
            "top_rate": rate,
            "top_n": top_n,
            "top_precision": round(float(top_y.mean()), 6),
            "top_recall": round(float(top_y.sum() / total_pos), 6)
            if total_pos > 0 else 0
        })

    return rows


def run_feature_selection_experiment(config):
    data_path = resolve_path(__file__, config["data_path"])
    importance_path = resolve_path(__file__, config["feature_importance_path"])
    output_dir = resolve_path(__file__, config["output_dir"])

    os.makedirs(output_dir, exist_ok=True)

    print("读取宽表：", data_path)
    df = pd.read_csv(data_path)

    print("读取特征重要性：", importance_path)
    importance = pd.read_csv(importance_path)

    target_col = config["target_col"]
    dataset_col = config["dataset_col"]
    drop_columns = set(config["drop_columns"])

    df[target_col] = pd.to_numeric(
        df[target_col],
        errors="coerce"
    ).fillna(0).astype("int8")

    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    all_features = [
        col for col in numeric_columns
        if col not in drop_columns
    ]

    ranked_features = [
        f for f in importance["feature"].tolist()
        if f in all_features
    ]

    feature_sets = {
        "all_features": all_features
    }

    for size in config["feature_set_sizes"]:
        feature_sets[f"top{size}_features"] = ranked_features[:size]

    train_df = df[df[dataset_col] == config["train_value"]].copy()
    valid_df = df[df[dataset_col] == config["valid_value"]].copy()
    test_df = df[df[dataset_col] == config["test_value"]].copy()

    metric_rows = []
    top_rows = []
    feature_list_rows = []
    models = {}

    for exp_name, features in feature_sets.items():
        print("开始实验：", exp_name, "特征数：", len(features))

        X_train, y_train = make_xy(train_df, features, target_col)
        X_valid, y_valid = make_xy(valid_df, features, target_col)
        X_test, y_test = make_xy(test_df, features, target_col)

        model = build_model(config)

        start = time.perf_counter()
        model.fit(X_train, y_train)
        train_time = time.perf_counter() - start

        valid_prob = model.predict_proba(X_valid)[:, 1]
        test_prob = model.predict_proba(X_test)[:, 1]

        metric_rows.append(
            evaluate_auc_pr(
                y_valid,
                valid_prob,
                config["valid_value"],
                exp_name,
                len(features),
                train_time
            )
        )

        metric_rows.append(
            evaluate_auc_pr(
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

        for rank, feature in enumerate(features, start=1):
            feature_list_rows.append({
                "experiment": exp_name,
                "feature_rank": rank,
                "feature": feature
            })

        models[exp_name] = model

    metrics_df = pd.DataFrame(metric_rows)
    top_df = pd.DataFrame(top_rows)
    feature_list_df = pd.DataFrame(feature_list_rows)

    summary_rows = []

    for exp_name in feature_sets.keys():
        valid_m = metrics_df[
            (metrics_df["experiment"] == exp_name) &
            (metrics_df["split"] == config["valid_value"])
        ].iloc[0]

        test_m = metrics_df[
            (metrics_df["experiment"] == exp_name) &
            (metrics_df["split"] == config["test_value"])
        ].iloc[0]

        test_top10 = top_df[
            (top_df["experiment"] == exp_name) &
            (top_df["split"] == config["test_value"]) &
            (top_df["top_rate"] == 0.10)
        ].iloc[0]

        summary_rows.append({
            "experiment": exp_name,
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
    summary_df = summary_df.sort_values(
        by=["test_pr_auc", "test_auc", "test_top10_precision"],
        ascending=False
    ).reset_index(drop=True)

    best_exp = summary_df.iloc[0]["experiment"]
    best_model = models[best_exp]

    summary_path = os.path.join(output_dir, "feature_selection_summary_with_path.csv")
    metrics_path = os.path.join(output_dir, "feature_selection_metrics_with_path.csv")
    top_path = os.path.join(output_dir, "feature_selection_top_rate_metrics_with_path.csv")
    feature_list_path = os.path.join(output_dir, "selected_feature_lists_with_path.csv")
    best_model_path = os.path.join(output_dir, f"best_model_{best_exp}.joblib")

    summary_df.to_csv(summary_path, index=False, encoding="utf-8-sig")
    metrics_df.to_csv(metrics_path, index=False, encoding="utf-8-sig")
    top_df.to_csv(top_path, index=False, encoding="utf-8-sig")
    feature_list_df.to_csv(feature_list_path, index=False, encoding="utf-8-sig")
    joblib.dump(best_model, best_model_path)

    return {
        "summary_path": summary_path,
        "metrics_path": metrics_path,
        "top_path": top_path,
        "feature_list_path": feature_list_path,
        "best_model_path": best_model_path,
        "best_experiment": best_exp
    }
