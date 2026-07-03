# XGBoost 购买概率模型工程

## 1. 本工程作用

本工程用于在新增行为路径特征后的宽表上训练 XGBoost 购买概率模型，并与 LR、LightGBM 进行对比。

默认测试：

```text
xgb_top20_no_weight
xgb_top20_scale_pos_weight
xgb_all_features_no_weight
xgb_all_features_scale_pos_weight
```

## 2. 输入文件

需要准备：

```text
ml_feature_wide_table_with_path.csv
selected_feature_lists_with_path.csv
```

## 3. 输出文件

```text
xgb_experiment_summary_with_path.csv
xgb_model_metrics_with_path.csv
xgb_top_rate_metrics_with_path.csv
xgb_feature_importance_with_path.csv
xgb_predictions_best_with_path.csv
best_xgb_model_xxx.joblib
best_xgb_features_xxx.csv
```

## 4. 运行方式

进入本项目文件夹后运行：

```bash
python run_xgb_model.py
```

## 5. 环境要求

需要安装 XGBoost：

```bash
python -m pip install xgboost
```
