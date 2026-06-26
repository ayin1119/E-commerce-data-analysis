CORE_USER_PURCHASE_CONFIG = {
    # 1. 原始用户行为数据路径
    "data_path": "../../../../../data_min.csv",

    # 2. RFM 用户分层结果表路径
    "rfm_path": "../../../../form/user/purchase_value/rfm/rfm_user_segment_from_three_tables.csv",

    # 3. 输出文件夹路径
    "output_dir": "../../../../form/item/item_user",

    # 4. 字段名配置
    "user_col": "user_id",
    "item_col": "item_id",
    "category_col": "item_category",
    "behavior_col": "behavior_type",
    "rfm_type_col": "rfm_type",

    # 5. 核心用户定义
    # 这里表示只把 RFM 类型为“重要价值用户”的用户当作核心用户
    "core_user_type": "重要价值用户",

    # 6. 购买行为编号
    "purchase_behavior_value": 4,

    # 7. 分块读取大小
    # 数据量大时不要一次性读完整张表，每次读取 50 万行
    "chunksize": 500000,

    # 8. 是否对最终结果完整排序
    # 时间复杂度优化点：
    # False 表示不做全量排序，整体更接近 O(N)
    "sort_result": False,

    # 9. 输出文件名
    "output_filename": "item_core_user_purchase_rate.csv"
}