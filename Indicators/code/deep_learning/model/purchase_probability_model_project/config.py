PURCHASE_MODEL_CONFIG = {
    # 1. 输入宽表路径
    # 这里用你已经生成并检查过的、含有 train/valid/test 和 label_buy_7d 的宽表
    "data_path": "../../../../form/deep_learning/ml_feature_wide_table_v1.csv",

    # 2. 输出文件夹
    "output_dir": "../../../../form/deep_learning",

    # 3. 数据集划分字段
    "dataset_col": "dataset_type",
    "train_value": "train",
    "valid_value": "valid",
    "test_value": "test",

    # 4. 目标标签
    "target_col": "label_buy_7d",

    # 5. 不进入模型的字段
    "drop_columns": [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d"
    ],

    # 6. 预测结果里要保留的字段
    "id_columns": [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d"
    ],

    # 7. 模型参数
    # 使用 SGD 逻辑回归：适合较大数据，按批次迭代，训练复杂度接近线性
    "random_state": 42,
    "max_iter": 1000,
    "tol": 0.001,
    "class_weight": "balanced",

    # 8. 是否把特征转成 float32，节省内存
    "use_float32": True,

    # 9. Top 比例评估
    "top_rates": [0.05, 0.10, 0.20],

    # 10. 特征重要性输出数量
    "top_n_features": 50,

    # 11. 输出文件名
    "model_filename": "purchase_probability_model.joblib",
    "metrics_filename": "model_metrics.csv",
    "top_rate_metrics_filename": "top_rate_metrics.csv",
    "feature_importance_filename": "feature_importance.csv",
    "prediction_filename": "purchase_probability_predictions.csv"
}
