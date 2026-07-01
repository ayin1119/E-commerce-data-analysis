# 购买概率模型：新增行为路径特征版本

## 1. 本版本修改内容

本版本基于新的 68 字段特征宽表进行修改。相较原 65 字段版本，本次新增了 3 个行为路径特征：

```text
pre_buy_behavior_count
purchase_count
pre_buy_behavior_per_purchase
```

这三个字段会自动进入模型训练，不需要手动写入特征列表。

## 2. 文件结构

```text
purchase_probability_model_with_path_project/
│
├── config.py
├── purchase_probability_pipeline.py
└── run_purchase_model.py
```

## 3. 使用前需要做什么

请把新版特征宽表：

```text
ml_feature_wide_table_with_path.csv
```

放到：

```text
E-commerce data analysis/Indicators/form/deep_learning/with_path/
```

如果你放在别的位置，只需要修改 `config.py` 中的：

```python
"data_path": "你的真实路径"
```

## 4. 输出结果

模型结果会输出到：

```text
E-commerce data analysis/Indicators/form/deep_learning/with_path/
```

输出文件包括：

```text
purchase_probability_model_with_path.joblib
model_metrics_with_path.csv
top_rate_metrics_with_path.csv
feature_importance_with_path.csv
purchase_probability_predictions_with_path.csv
```

## 5. 运行方式

进入项目文件夹后运行：

```bash
python run_purchase_model.py
```

不要直接运行 `purchase_probability_pipeline.py`。

## 6. 本次检查逻辑

代码会检查这三个新增行为路径特征是否存在：

```text
pre_buy_behavior_count
purchase_count
pre_buy_behavior_per_purchase
```

如果宽表没有这些字段，会直接报错，防止误用旧版 65 字段宽表。
