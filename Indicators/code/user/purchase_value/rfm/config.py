RFM_CONFIG = {
    # 1. 三个输入文件路径
    "last_purchase_path": "../../../../form/user/purchase_value/The_most_recent_purchase_date.csv",
    "purchase_freq_path": "../../../../form/user/purchase_value/frequency.csv",
    "purchase_value_path": "../../../../form/user/purchase_value/volume_and_rate.csv",

    # 2. 输出文件夹路径：结果会保存到这个文件夹
    "output_dir": "../../../../form/user/purchase_value/rfm",

    # 3. 三张表共同的用户编号字段
    "merge_key": "user_id",

    # 4. R/F/M 分成几档：5 表示 1~5 分
    "score_bins": 5,

    # 5. 需要转成数字的列
    "numeric_columns": [
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
    ],

    # 6. 输出结果需要保留的列
    "output_columns": [
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
    ],

    # 7. 用户分层顺序：只是为了让汇总表按我们想要的顺序展示
    "type_order": [
        "重要价值用户",
        "重要保持用户",
        "重要发展用户",
        "重要潜力用户",
        "一般价值用户",
        "一般保持用户",
        "一般发展用户",
        "低价值用户",
        "未购买用户"
    ],

    # 8. 输出文件名
    "user_result_filename": "rfm_user_segment_from_three_tables.csv",
    "summary_filename": "rfm_segment_summary_from_three_tables.csv"
}
