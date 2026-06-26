# %%
import pandas as pd
import numpy as np
import os

last_purchase_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/最近一次购买时间.csv"
purchase_freq_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/购买频率.csv"
purchase_value_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/购买数，购买率.csv"

output_dir = "/Users/ayin/Desktop/rfm_output"
os.makedirs(output_dir, exist_ok=True)

last_purchase = pd.read_csv(last_purchase_path)
purchase_freq = pd.read_csv(purchase_freq_path)
purchase_value = pd.read_csv(purchase_value_path)

df = last_purchase.merge(
    purchase_freq,
    on="user_id",
    how="outer"
)

df = df.merge(
    purchase_value,
    on="user_id",
    how="outer"
)

num_cols = [
    "days_since_last_purchase",
    "purchase_day_frequency",
    "purchase_count",
    "purchase_days",
    "avg_days_per_purchase_day",
    "hours_since_last_purchase",
    "total_behavior_count",
    "distinct_purchase_item_count",
    "purchase_rate",
    "total_purchase_count"
]

for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

purchase_users = df[df["purchase_count"].fillna(0) > 0].copy()
non_purchase_users = df[df["purchase_count"].fillna(0) <= 0].copy()


purchase_users["R_score"] = pd.qcut(
    purchase_users["days_since_last_purchase"].rank(method="first"),
    q=5,
    labels=[5, 4, 3, 2, 1]
).astype(float)

purchase_users["F_score"] = pd.qcut(
    purchase_users["purchase_day_frequency"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(float)

purchase_users["M_score"] = pd.qcut(
    purchase_users["purchase_count"].rank(method="first"),
    q=5,
    labels=[1, 2, 3, 4, 5]
).astype(float)

r_mean = purchase_users["R_score"].mean()
f_mean = purchase_users["F_score"].mean()
m_mean = purchase_users["M_score"].mean()

purchase_users["R_level"] = np.where(
    purchase_users["R_score"] > r_mean,
    "高",
    "低"
)

purchase_users["F_level"] = np.where(
    purchase_users["F_score"] > f_mean,
    "高",
    "低"
)

purchase_users["M_level"] = np.where(
    purchase_users["M_score"] > m_mean,
    "高",
    "低"
)

def classify_rfm(row):
    r = row["R_level"]
    f = row["F_level"]
    m = row["M_level"]

    if r == "高" and f == "高" and m == "高":
        return "重要价值用户"
    elif r == "低" and f == "高" and m == "高":
        return "重要保持用户"
    elif r == "高" and f == "低" and m == "高":
        return "重要发展用户"
    elif r == "高" and f == "高" and m == "低":
        return "重要潜力用户"
    elif r == "高" and f == "低" and m == "低":
        return "一般价值用户"
    elif r == "低" and f == "高" and m == "低":
        return "一般保持用户"
    elif r == "低" and f == "低" and m == "高":
        return "一般发展用户"
    else:
        return "低价值用户"

purchase_users["rfm_type"] = purchase_users.apply(classify_rfm, axis=1)

non_purchase_users["R_score"] = np.nan
non_purchase_users["F_score"] = np.nan
non_purchase_users["M_score"] = np.nan

non_purchase_users["R_level"] = "未购买"
non_purchase_users["F_level"] = "未购买"
non_purchase_users["M_level"] = "未购买"

non_purchase_users["rfm_type"] = "未购买用户"


rfm_result = pd.concat(
    [purchase_users, non_purchase_users],
    ignore_index=True
)

output_cols = [
    "user_id",
    "days_since_last_purchase",
    "purchase_day_frequency",
    "purchase_count",
    "R_score",
    "F_score",
    "M_score",
    "R_level",
    "F_level",
    "M_level",
    "rfm_type",
    "purchase_days",
    "avg_days_per_purchase_day",
    "last_purchase_time",
    "survey_end_time",
    "hours_since_last_purchase",
    "total_behavior_count",
    "distinct_purchase_item_count",
    "purchase_rate",
    "total_purchase_count"
]

output_cols = [col for col in output_cols if col in rfm_result.columns]

rfm_result = rfm_result[output_cols]

rfm_summary = (
    rfm_result
    .groupby("rfm_type")
    .agg(
        user_count=("user_id", "count"),
        avg_days_since_last_purchase=("days_since_last_purchase", "mean"),
        avg_purchase_day_frequency=("purchase_day_frequency", "mean"),
        avg_purchase_count=("purchase_count", "mean"),
        avg_purchase_rate=("purchase_rate", "mean"),
        avg_purchase_days=("purchase_days", "mean")
    )
    .reset_index()
)

rfm_summary["user_rate"] = (
    rfm_summary["user_count"] / rfm_summary["user_count"].sum()
).round(4)

type_order = [
    "重要价值用户",
    "重要保持用户",
    "重要发展用户",
    "重要潜力用户",
    "一般价值用户",
    "一般保持用户",
    "一般发展用户",
    "低价值用户",
    "未购买用户"
]

rfm_summary["type_order"] = rfm_summary["rfm_type"].apply(
    lambda x: type_order.index(x) if x in type_order else 999
)

rfm_summary = (
    rfm_summary
    .sort_values("type_order")
    .drop(columns="type_order")
)

rfm_result.to_csv(
    os.path.join(output_dir, "rfm_user_segment_from_three_tables.csv"),
    index=False,
    encoding="utf-8-sig"
)

rfm_summary.to_csv(
    os.path.join(output_dir, "rfm_segment_summary_from_three_tables.csv"),
    index=False,
    encoding="utf-8-sig"
)



