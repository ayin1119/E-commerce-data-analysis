PURCHASE_MODEL_CONFIG = {
    # 1. 输入宽表路径
    # 这里改成新增行为路径特征后的 68 字段宽表
    # 请把 ml_feature_wide_table_with_path.csv 放到这个目录下：
    # E-commerce data analysis/Indicators/form/deep_learning/with_path/
    "data_path": "../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv",

    # 2. 输出文件夹
    # 新模型结果单独保存，避免覆盖旧的 65 字段版本结果
    "output_dir": "../../../../form/deep_learning/with_path",

    # 3. 数据集划分字段
    "dataset_col": "dataset_type",
    "train_value": "train",
    "valid_value": "valid",
    "test_value": "test",

    # 4. 目标标签
    "target_col": "label_buy_7d",

    # 5. 不进入模型的字段
    # 这些是样本标识字段和目标标签，不能作为模型输入特征
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

    # 7. 新增行为路径特征字段
    # 这三个字段必须存在于新版特征宽表中
    "required_feature_columns": [
        "pre_buy_behavior_count",
        "purchase_count",
        "pre_buy_behavior_per_purchase"
    ],

    # 8. 模型参数
    # 使用 SGD 逻辑回归：适合较大数据，按批次迭代，训练复杂度接近线性
    "random_state": 42,
    "max_iter": 1000,
    "tol": 0.001,
    "class_weight": "balanced",

    # 9. 是否把特征转成 float32，节省内存
    "use_float32": True,

    # 10. Top 比例评估
    "top_rates": [0.05, 0.10, 0.20],

    # 11. 特征重要性输出数量
    "top_n_features": 50,

    # 12. 输出文件名
    # 文件名加 with_path，方便和旧模型结果区分
    "model_filename": "purchase_probability_model_with_path.joblib",
    "metrics_filename": "model_metrics_with_path.csv",
    "top_rate_metrics_filename": "top_rate_metrics_with_path.csv",
    "feature_importance_filename": "feature_importance_with_path.csv",
    "prediction_filename": "purchase_probability_predictions_with_path.csv"
}
