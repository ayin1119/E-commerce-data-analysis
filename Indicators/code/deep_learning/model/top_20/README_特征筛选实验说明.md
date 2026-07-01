# 68 字段购买概率模型：特征筛选实验模块

## 1. 模块作用

本模块用于比较不同特征数量下模型效果是否稳定。

会自动测试：

```text
全部特征
Top50 特征
Top40 特征
Top30 特征
Top20 特征
```

## 2. 输入文件

```text
ml_feature_wide_table_with_path.csv
feature_importance_with_path.csv
```

## 3. 输出文件

```text
feature_selection_summary_with_path.csv
feature_selection_metrics_with_path.csv
feature_selection_top_rate_metrics_with_path.csv
selected_feature_lists_with_path.csv
best_model_xxx.joblib
```

## 4. 运行方式

进入本项目文件夹后运行：

```bash
python run_feature_selection.py
```
