# LightGBM 购买概率模型工程

## 1. 本工程作用

本工程用于在新增行为路径特征后的宽表上训练 LightGBM 购买概率模型，并和原来的逻辑回归版本做对比。

默认会测试：

```text
lgbm_top20_no_weight
lgbm_top20_scale_pos_weight
lgbm_all_features_no_weight
lgbm_all_features_scale_pos_weight
```

## 2. 输入文件

需要准备：

```text
ml_feature_wide_table_with_path.csv
selected_feature_lists_with_path.csv
feature_selection_summary_with_path.csv
```

其中 `selected_feature_lists_with_path.csv` 用于读取 Top20 特征。

## 3. 输出文件

运行后会输出：

```text
lgbm_experiment_summary_with_path.csv
lgbm_model_metrics_with_path.csv
lgbm_top_rate_metrics_with_path.csv
lgbm_feature_importance_with_path.csv
lgbm_predictions_best_with_path.csv
best_lgbm_model_xxx.joblib
best_lgbm_features_xxx.csv
```

## 4. 运行方式

进入本项目文件夹后运行：

```bash
python run_lgbm_model.py
```

## 5. 环境要求

需要安装 LightGBM：

```bash
python -m pip install lightgbm
```
