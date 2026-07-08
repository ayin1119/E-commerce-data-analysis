XGB_CALIBRATION_CONFIG = {
    # 1. 输入：XGBoost 最优模型预测结果
    # 该文件来自 XGBoost 模型工程输出：
    # xgb_predictions_best_with_path.csv
    "prediction_path": "../../../../form/deep_learning/with_path/xgboost/xgb_predictions_best_with_path.csv",

    # 2. 输出目录
    # 校准结果单独保存，避免覆盖原始 XGBoost 结果
    "output_dir": "../../../../form/deep_learning/with_path/xgboost_calibration",

    # 3. 字段配置
    "dataset_col": "dataset_type",
    "valid_value": "valid",
    "test_value": "test",
    "target_col": "label_buy_7d",

    # 4. 原始 XGBoost 概率字段
    "probability_col": "xgb_probability",

    # 5. 校准配置
    # valid 集用于拟合校准器，valid/test 都会输出校准后概率
    "n_bins": 10,
    "top_rates": [0.05, 0.10, 0.20],

    # 6. 默认推荐概率
    # 根据校准报告，Platt 更适合作为业务解释概率
    # 程序会额外生成 calibrated_xgb_probability = platt_xgb_probability
    "default_calibrated_method": "platt",

    # 7. 输出文件
    "calibrated_prediction_filename": "calibrated_xgb_predictions_with_path.csv",
    "calibration_metrics_filename": "xgb_calibration_metrics_with_path.csv",
    "calibration_bin_report_filename": "xgb_calibration_bin_report_with_path.csv",
    "calibration_top_rate_filename": "xgb_calibration_top_rate_metrics_with_path.csv",
    "calibrator_filename": "xgb_probability_calibrators_with_path.joblib"
}
