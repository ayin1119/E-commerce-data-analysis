USER_CHURN_CONFIG = {
    # 1. 输入文件路径
    "input_path": "../../../../form/user/purchase_value/The_most_recent_purchase_date.csv",

    # 2. 输出文件夹路径
    "output_dir": "../../../../form/user/Retention_Repeat_Purchase/Lost_users",

    # 3. 字段名配置
    "user_col": "user_id",
    "days_col": "days_since_last_purchase",
    "hours_col": "hours_since_last_purchase",

    # 4. 流失用户比例
    # 距离上次购买时间最长的前 20% 用户，标记为“流失用户”
    "churn_ratio": 0.2,

    # 5. 流失倾向用户比例
    # 距离上次购买时间最长的前 50% 用户中，去掉前 20%，剩下 20%~50% 标记为“有流失倾向用户”
    "risk_ratio": 0.5,

    # 6. 是否保留完整排名
    # False：不做全量排序，时间复杂度更低，推荐
    # True：保留 user_rank 和 rank_rate，但会做完整排序，复杂度为 O(n log n)
    "keep_rank": False,

    # 7. 输出文件名
    "output_filename": "user_churn_result.csv"
}