# %%
import pandas as pd
import os

data_path = "/Users/ayin/Desktop/MYSQL/data_min.csv"
rfm_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/rfm分析/rfm_user_segment_from_three_tables.csv"

output_dir = "/Users/ayin/Desktop/rfm_top100商品"
os.makedirs(output_dir, exist_ok=True)

rfm = pd.read_csv(rfm_path)

rfm["user_id"] = rfm["user_id"].astype(str)

rfm = rfm[["user_id", "rfm_type"]].drop_duplicates()

result_list = []

for chunk in pd.read_csv(
    data_path,
    usecols=["user_id", "item_id", "item_category", "behavior_type"],
    chunksize=500000
):
    chunk["user_id"] = chunk["user_id"].astype(str)

    purchase_chunk = chunk[chunk["behavior_type"] == 4].copy()

    if purchase_chunk.empty:
        continue

    purchase_with_rfm = purchase_chunk.merge(
        rfm,
        on="user_id",
        how="left"
    )

    purchase_with_rfm["rfm_type"] = purchase_with_rfm["rfm_type"].fillna("未知用户")

    temp = (
        purchase_with_rfm
        .groupby(["rfm_type", "item_category", "item_id"])
        .agg(
            purchase_count=("behavior_type", "count"),
            purchase_user_count=("user_id", "nunique")
        )
        .reset_index()
    )

    result_list.append(temp)

rfm_item_purchase = pd.concat(result_list, ignore_index=True)

rfm_item_purchase = (
    rfm_item_purchase
    .groupby(["rfm_type", "item_category", "item_id"])
    .agg(
        purchase_count=("purchase_count", "sum"),
        purchase_user_count=("purchase_user_count", "sum")
    )
    .reset_index()
)


rfm_total_purchase = (
    rfm_item_purchase
    .groupby("rfm_type")["purchase_count"]
    .sum()
    .reset_index(name="rfm_total_purchase_count")
)

rfm_item_purchase = rfm_item_purchase.merge(
    rfm_total_purchase,
    on="rfm_type",
    how="left"
)

rfm_item_purchase["purchase_share_in_rfm"] = (
    rfm_item_purchase["purchase_count"]
    / rfm_item_purchase["rfm_total_purchase_count"]
).round(4)


rfm_item_purchase["item_rank"] = (
    rfm_item_purchase
    .groupby("rfm_type")["purchase_count"]
    .rank(method="first", ascending=False)
    .astype(int)
)


rfm_top100_item = (
    rfm_item_purchase
    .sort_values(
        by=["rfm_type", "purchase_count", "purchase_user_count"],
        ascending=[True, False, False]
    )
)

rfm_top100_item = rfm_top100_item[
    rfm_top100_item["item_rank"] <= 100
].copy()


output_path = os.path.join(
    output_dir,
    "rfm_each_level_top100_items.csv"
)

rfm_top100_item.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("RFM各层级Top100商品表已生成：")
print(output_path)

print(rfm_top100_item.head())


