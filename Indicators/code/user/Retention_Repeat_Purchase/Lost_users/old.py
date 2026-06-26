# %%
import pandas as pd
import numpy as np

df = pd.read_csv("/Users/ayin/Desktop/最近一次购买时间.csv")

valid = df[df["days_since_last_purchase"].notna()].copy()

valid = valid.sort_values(
    by=["days_since_last_purchase", "hours_since_last_purchase", "user_id"],
    ascending=[False, False, True]
).reset_index(drop=True)

valid["user_rank"] = np.arange(1, len(valid) + 1)
valid["total_users"] = len(valid)
valid["rank_rate"] = valid["user_rank"] / valid["total_users"]

valid["churn_type"] = np.where(
    valid["rank_rate"] <= 0.2,
    "流失用户",
    np.where(
        valid["rank_rate"] <= 0.5,
        "有流失倾向用户",
        None
    )
)

churn_result = valid[valid["churn_type"].notna()].copy()

churn_result.to_csv(
    "/Users/ayin/Desktop/user_churn_result.csv",
    index=False,
    encoding="utf-8-sig"
)

print(churn_result["churn_type"].value_counts())


