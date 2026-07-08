LGBM_CALIBRATION_CONFIG = {
    # 输入：LightGBM 最优模型预测结果
    "prediction_path": "../../../../form/deep_learning/with_path/lgbm/lgbm_predictions_best_with_path.csv",

    # 输出目录
    "output_dir": "../../../../form/deep_learning/with_path/lgbm_calibration",

    # 字段配置
    "dataset_col": "dataset_type",
    "valid_value": "valid",
    "test_value": "test",
    "target_col": "label_buy_7d",
    "probability_col": "lgbm_probability",

    # 校准配置
    "n_bins": 10,
    "top_rates": [0.05, 0.10, 0.20],

    # 输出文件
    "calibrated_prediction_filename": "calibrated_lgbm_predictions_with_path.csv",
    "calibration_metrics_filename": "lgbm_calibration_metrics_with_path.csv",
    "calibration_bin_report_filename": "lgbm_calibration_bin_report_with_path.csv",
    "calibration_top_rate_filename": "lgbm_calibration_top_rate_metrics_with_path.csv",
    "calibrator_filename": "lgbm_probability_calibrators_with_path.joblib"
}
