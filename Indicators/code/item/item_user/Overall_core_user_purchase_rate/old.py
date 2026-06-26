# %%
import pandas as pd

data_path = "/Users/ayin/Desktop/MYSQL/data_min.csv"
rfm_path = "/Users/ayin/Desktop/阿里/代码/表/用户/用户购买价值/rfm分析/rfm_user_segment_from_three_tables.csv"

rfm = pd.read_csv(rfm_path)

rfm["user_id"] = rfm["user_id"].astype(str)

high_value_users = set(
    rfm.loc[
        rfm["rfm_type"] == "重要价值用户",
        "user_id"
    ]
)

total_purchase_count = 0
high_value_purchase_count = 0

for chunk in pd.read_csv(
    data_path,
    usecols=["user_id", "behavior_type"],
    chunksize=500000
):
    chunk["user_id"] = chunk["user_id"].astype(str)

    purchase_chunk = chunk[chunk["behavior_type"] == 4]

    total_purchase_count += len(purchase_chunk)

    high_value_purchase_count += purchase_chunk[
        purchase_chunk["user_id"].isin(high_value_users)
    ].shape[0]

high_value_purchase_ratio = (
    high_value_purchase_count / total_purchase_count
    if total_purchase_count != 0
    else 0
)

core_user_purchase_result = pd.DataFrame({
    "核心用户类型": ["重要价值用户"],
    "核心用户人数": [len(high_value_users)],
    "全体购买次数": [total_purchase_count],
    "核心用户购买次数": [high_value_purchase_count],
    "核心用户购买贡献率": [round(high_value_purchase_ratio, 4)],
    "核心用户购买贡献率_百分比": [f"{high_value_purchase_ratio * 100:.2f}%"]
})

print(core_user_purchase_result)

core_user_purchase_result.to_csv(
    "/Users/ayin/Desktop/core_user_purchase_result.csv",
    index=False,
    encoding="utf-8-sig"
)



