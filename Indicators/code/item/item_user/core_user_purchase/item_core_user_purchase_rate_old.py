# %%
import pandas as pd
import os

data_path = "/Users/ayin/Desktop/MYSQL/data_min.csv"
rfm_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/rfm分析/rfm_user_segment_from_three_tables.csv"

output_dir = "/Users/ayin/Desktop/商品核心用户购买率"
os.makedirs(output_dir, exist_ok=True)


rfm = pd.read_csv(rfm_path)

rfm["user_id"] = rfm["user_id"].astype(str)

# 核心用户：重要价值用户
core_users = set(
    rfm.loc[
        rfm["rfm_type"] == "重要价值用户",
        "user_id"
    ].astype(str)
)

print("核心用户数量：", len(core_users))


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

    purchase_chunk["is_core_user"] = purchase_chunk["user_id"].isin(core_users).astype(int)

    temp = (
        purchase_chunk
        .groupby(["item_category", "item_id"])
        .agg(
            total_purchase_count=("behavior_type", "count"),
            core_user_purchase_count=("is_core_user", "sum")
        )
        .reset_index()
    )

    result_list.append(temp)


item_core_purchase = pd.concat(result_list, ignore_index=True)

item_core_purchase = (
    item_core_purchase
    .groupby(["item_category", "item_id"])
    .agg(
        total_purchase_count=("total_purchase_count", "sum"),
        core_user_purchase_count=("core_user_purchase_count", "sum")
    )
    .reset_index()
)


item_core_purchase["non_core_user_purchase_count"] = (
    item_core_purchase["total_purchase_count"]
    - item_core_purchase["core_user_purchase_count"]
)

item_core_purchase["core_user_purchase_rate"] = (
    item_core_purchase["core_user_purchase_count"]
    / item_core_purchase["total_purchase_count"]
).round(4)

item_core_purchase["core_user_purchase_rate_percent"] = (
    item_core_purchase["core_user_purchase_rate"] * 100
).round(2).astype(str) + "%"


item_core_purchase = item_core_purchase.sort_values(
    by=["item_category", "core_user_purchase_rate", "total_purchase_count"],
    ascending=[True, False, False]
)

output_path = os.path.join(output_dir, "item_core_user_purchase_rate.csv")

item_core_purchase.to_csv(
    output_path,
    index=False,
    encoding="utf-8-sig"
)

print("商品核心用户购买率表已生成：")
print(output_path)

print(item_core_purchase.head())


