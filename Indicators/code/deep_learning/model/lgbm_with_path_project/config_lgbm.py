LGBM_CONFIG = {
    # 输入文件
    "data_path": "../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv",
    "selected_feature_path": "../../../../form/deep_learning/with_path/feature_selection/selected_feature_lists_with_path.csv",
    "lr_summary_path": "../../../../form/deep_learning/with_path/feature_selection/feature_selection_summary_with_path.csv",

    # 输出目录
    "output_dir": "../../../../form/deep_learning/with_path/lgbm",

    # 字段配置
    "dataset_col": "dataset_type",
    "train_value": "train",
    "valid_value": "valid",
    "test_value": "test",
    "target_col": "label_buy_7d",

    # 非建模字段
    "drop_columns": [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d"
    ],

    # 预测结果保留字段
    "id_columns": [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d"
    ],

    # LightGBM 参数
    "random_state": 42,
    "n_estimators": 160,
    "learning_rate": 0.06,
    "num_leaves": 15,
    "max_depth": 5,
    "min_child_samples": 60,
    "subsample": 0.85,
    "subsample_freq": 1,
    "colsample_bytree": 0.85,
    "reg_alpha": 0.0,
    "reg_lambda": 1.0,
    "max_bin": 63,
    "n_jobs": 2,

    # 实验配置
    "top_rates": [0.05, 0.10, 0.20],
    "run_feature_sets": ["top20", "all_features"],
    "run_weight_options": ["no_weight", "scale_pos_weight"]
}
