TOP10_CATEGORY_CONFIG = {
    # 1. 原始行为数据表路径
    "data_path": "../../../../data_min.csv",

    # 2. RFM 用户分层结果表路径
    "rfm_path": "../../../form/user/purchase_value/rfm/rfm_user_segment_from_three_tables.csv",

    # 3. 输出文件夹路径
    "output_dir": "../../../form/item/category_performance/",

    # 4. 字段名配置
    "user_col": "user_id",
    "category_col": "item_category",
    "behavior_col": "behavior_type",
    "rfm_type_col": "rfm_type",

    # 5. 购买行为的编号
    "purchase_behavior_value": 4,

    # 6. 分块读取大小
    "chunksize": 500000,

    # 7. 每个 RFM 层级取前几个商品类别
    # 这里是 Top10
    "top_k": 10,

    # 8. 输出文件名
    "output_filename": "rfm_each_level_top10_categories.csv"
}