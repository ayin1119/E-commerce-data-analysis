RFM_TOP100_ITEM_CONFIG = {
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

    # 5. 购买行为编号
    # 你的数据中 behavior_type = 4 表示购买
    "purchase_behavior_value": 4,

    # 6. 未匹配到 RFM 分层的用户，统一标记为未知用户
    "unknown_user_label": "未知用户",

    # 7. 分块读取大小
    # 数据量大时不要一次性读完整张表，每次读取 50 万行
    "chunksize": 500000,

    # 8. 每个 RFM 层级取前多少个商品
    # 这里是 Top100
    "top_k": 100,

    # 9. 输出文件名
    "output_filename": "rfm_each_level_top100_items.csv"
}