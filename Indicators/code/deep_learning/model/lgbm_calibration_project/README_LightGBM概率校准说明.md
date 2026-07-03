# LightGBM 概率校准工程

## 1. 工程作用

本工程用于对 LightGBM 最优模型输出的购买概率进行校准。

输入文件：

```text
lgbm_predictions_best_with_path.csv
```

输出文件：

```text
calibrated_lgbm_predictions_with_path.csv
lgbm_calibration_metrics_with_path.csv
lgbm_calibration_bin_report_with_path.csv
lgbm_calibration_top_rate_metrics_with_path.csv
lgbm_probability_calibrators_with_path.joblib
```

## 2. 校准方法

本工程使用：

```text
Platt Scaling
Isotonic Regression
```

## 3. 运行方式

进入项目文件夹后运行：

```bash
python run_lgbm_calibration.py
```

## 4. 使用建议

排序场景使用：

```text
original_lgbm_probability
```

概率解释场景使用：

```text
platt_lgbm_probability
```
