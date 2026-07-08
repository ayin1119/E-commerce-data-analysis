# XGBoost 概率校准工程

## 1. 工程作用

本工程用于对 XGBoost 最优模型输出的购买概率进行校准。

输入文件：

```text
xgb_predictions_best_with_path.csv
```

该文件需要包含：

```text
dataset_type
label_buy_7d
xgb_probability
```

## 2. 校准方法

本工程同时输出三类概率：

```text
original_xgb_probability
platt_xgb_probability
isotonic_xgb_probability
```

并额外输出一个默认推荐字段：

```text
calibrated_xgb_probability
```

当前默认：

```text
calibrated_xgb_probability = platt_xgb_probability
```

原因是 Platt Scaling 通常更加稳定，适合业务购买概率解释。

## 3. 输出文件

运行后会输出：

```text
calibrated_xgb_predictions_with_path.csv
xgb_calibration_metrics_with_path.csv
xgb_calibration_bin_report_with_path.csv
xgb_calibration_top_rate_metrics_with_path.csv
xgb_probability_calibrators_with_path.joblib
```

## 4. 运行方式

进入项目文件夹后运行：

```bash
python run_xgb_calibration.py
```

## 5. 使用建议

| 使用场景 | 推荐字段 | 说明 |
|---|---|---|
| 推荐排序、Top 用户商品筛选 | original_xgb_probability | 保留原始排序分数 |
| 业务购买概率解释 | calibrated_xgb_probability 或 platt_xgb_probability | 概率更接近真实购买率 |
| 校准对照分析 | isotonic_xgb_probability | 用于辅助比较 |

## 6. 指标说明

输出指标包括：

```text
AUC
PR-AUC
Brier Score
Log Loss
ECE
MCE
Top Precision
Top Recall
```

其中 AUC、PR-AUC 主要看排序能力；Brier Score、Log Loss、ECE、MCE 主要看概率是否可信。
