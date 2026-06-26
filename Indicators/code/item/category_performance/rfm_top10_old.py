# %%
import pandas as pd
import os

data_path = "/Users/ayin/Desktop/MYSQL/data_min.csv"
rfm_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/rfm分析/rfm_user_segment_from_three_tables.csv"

output_dir = "/Users/ayin/Desktop/rfm_top10类别"
os.makedirs(output_dir, exist_ok=True)

rfm = pd.read_csv(rfm_path, usecols=["user_id", "rfm_type"])

rfm["user_id"] = rfm["user_id"].astype(str)

rfm = rfm.drop_duplicates(subset=["user_id"])

purchase_count_list = []
unique_user_category_list = []

for chunk in pd.read_csv(
    data_path,
    usecols=["user_id", "item_category", "behavior_type"],
    chunksize=500000
):
    chunk["user_id"] = chunk["user_id"].astype(str)
    chunk["behavior_type"] = pd.to_numeric(chunk["behavior_type"], errors="coerce")

    purchase_chunk = chunk[chunk["behavior_type"] == 4].copy()

    if purchase_chunk.empty:
        continue

    purchase_with_rfm = purchase_chunk.merge(
        rfm,
        on="user_id",
        how="left"
    )

    purchase_with_rfm["rfm_type"] = purchase_with_rfm["rfm_type"].fillna("未知用户")

    temp_count = (
        purchase_with_rfm
        .groupby(["rfm_type", "item_category"])
        .size()
        .reset_index(name="purchase_count")
    )

    purchase_count_list.append(temp_count)

    temp_user_category = purchase_with_rfm[
        ["rfm_type", "item_category", "user_id"]
    ].drop_duplicates()

    unique_user_category_list.append(temp_user_category)

rfm_category_purchase = pd.concat(purchase_count_list, ignore_index=True)

rfm_category_purchase = (
    rfm_category_purchase
    .groupby(["rfm_type", "item_category"])
    .agg(
        purchase_count=("purchase_count", "sum")
    )
    .reset_index()
)

unique_user_category = pd.concat(unique_user_category_list, ignore_index=True)

unique_user_category = unique_user_category.drop_duplicates(
    subset=["rfm_type", "item_category", "user_id"]
)

purchase_user_count = (
    unique_user_category
    .groupby(["rfm_type", "item_category"])
    .agg(
        purchase_user_count=("user_id", "nunique")
    )
    .reset_index()
)

rfm_category_purchase = rfm_category_purchase.merge(
    purchase_user_count,
    on=["rfm_type", "item_category"],
    how="left"
)

rfm_total_purchase = (
    rfm_category_purchase
    .groupby("rfm_type")
    .agg(
        rfm_total_purchase_count=("purchase_count", "sum")
    )
    .reset_index()
)

rfm_category_purchase = rfm_category_purchase.merge(
    rfm_total_purchase,
    on="rfm_type",
    how="left"
)
rfm_purchase_user = (
    unique_user_category
    .drop_duplicates(subset=["rfm_type", "user_id"])
    .groupby("rfm_type")
    .agg(
        rfm_purchase_user_count=("user_id", "nunique")
    )
    .reset_index()
)

rfm_category_purchase = rfm_category_purchase.merge(
    rfm_purchase_user,
    on="rfm_type",
    how="left"
)

rfm_category_purchase["category_purchase_share"] = (
    rfm_category_purchase["purchase_count"]
    / rfm_category_purchase["rfm_total_purchase_count"]
).round(4)

rfm_category_purchase["category_purchase_share_percent"] = (
    rfm_category_purchase["category_purchase_share"] * 100
).round(2).astype(str) + "%"

rfm_category_purchase["category_user_share"] = (
    rfm_category_purchase["purchase_user_count"]
    / rfm_category_purchase["rfm_purchase_user_count"]
).round(4)

rfm_category_purchase["category_user_share_percent"] = (
    rfm_category_purchase["category_user_share"] * 100
).round(2).astype(str) + "%"


rfm_category_purchase = rfm_category_purchase.sort_values(
    by=["rfm_type", "purchase_count", "purchase_user_count"],
    ascending=[True, False, False]
)

rfm_category_purchase["category_rank"] = (
    rfm_category_purchase
    .groupby("rfm_type")
    .cumcount() + 1
)

rfm_top10_category = rfm_category_purchase[
    rfm_category_purchase["category_rank"] <= 10
].copy()

rfm_top10_category = rfm_top10_category[
    [
        "rfm_type",
        "category_rank",
        "item_category",
        "purchase_count",
        "purchase_user_count",
        "rfm_total_purchase_count",
        "rfm_purchase_user_count",
        "category_purchase_share",
        "category_purchase_share_percent",
        "category_user_share",
        "category_user_share_percent"
    ]
]

output_path = os.path.join(
    output_dir,
    "rfm_each_level_top10_categories.csv"
)

rfm_top10_category.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("RFM各层级Top10购买类别表已生成：")
print(output_path)

print(rfm_top10_category.head(20))


