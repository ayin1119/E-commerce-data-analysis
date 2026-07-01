FEATURE_SELECTION_CONFIG = {
    # 输入文件
    "data_path": "../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv",
    "feature_importance_path": "../../../../form/deep_learning/with_path/feature_importance_with_path.csv",

    # 输出目录
    "output_dir": "../../../../form/deep_learning/top_20/feature_selection",

    # 字段配置
    "dataset_col": "dataset_type",
    "train_value": "train",
    "valid_value": "valid",
    "test_value": "test",
    "target_col": "label_buy_7d",

    # 不进入模型的字段
    "drop_columns": [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d"
    ],

    # 特征筛选实验版本
    "feature_set_sizes": [50, 40, 30, 20],

    # 模型参数
    "random_state": 42,
    "max_iter": 1000,
    "tol": 0.001,
    "class_weight": "balanced",

    # Top比例
    "top_rates": [0.05, 0.10, 0.20]
}
