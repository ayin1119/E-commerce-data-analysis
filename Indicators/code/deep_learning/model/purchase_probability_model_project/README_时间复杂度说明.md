# 购买概率模型代码封装与时间复杂度优化说明

## 1. 项目目标

本项目目标是训练一个购买概率模型，用于预测用户未来 7 天是否购买某个商品。

目标标签为：

```text
label_buy_7d
```

其中：

```text
1 = 未来 7 天购买
0 = 未来 7 天未购买
```

模型输出为：

```text
buy_probability
```

表示用户未来 7 天购买该商品的概率。

## 2. 封装后的项目结构

```text
purchase_probability_model_project/
│
├── config.py
├── purchase_probability_pipeline.py
├── run_purchase_model.py
└── README_时间复杂度说明.md
```

## 3. 文件作用

| 文件 | 作用 |
|---|---|
| `config.py` | 配置参数文件，保存输入路径、输出路径、目标标签、模型参数和输出文件名 |
| `purchase_probability_pipeline.py` | 核心代码封装文件，包含读取数据、特征选择、模型训练、预测、评估和保存结果 |
| `run_purchase_model.py` | 运行入口文件，负责调用统一接口 |
| `README_时间复杂度说明.md` | 说明代码封装和时间复杂度优化 |

## 4. 接口定义

统一接口为：

```python
run_purchase_probability_model(config)
```

该接口完成完整流程：

```text
读取数据
→ 检查字段
→ 自动选择特征
→ 划分 train / valid / test
→ 训练购买概率模型
→ 预测购买概率
→ 计算 AUC、PR-AUC
→ 计算 Top 比例命中效果
→ 保存模型和结果
```

## 5. 时间复杂度符号

设：

```text
n = 训练样本数量
m = 验证集或测试集样本数量
d = 特征数量
T = 模型迭代轮数
k = TopK 样本数量
```

## 6. 原始简单写法的复杂度问题

普通写法通常会：

```text
1. 一次性读取全部字段
2. 手动写训练、预测、评估代码
3. 使用完整排序计算 Top10% 命中率
4. 使用普通 LogisticRegression 训练
```

其中，完整排序评估 Top10% 的复杂度是：

```text
O(m log m)
```

如果只是看前 10% 样本，其实没必要完整排序。

## 7. 本次优化点

### 7.1 自动选择数值特征

代码会自动排除：

```text
dataset_type
snapshot_date
user_id
item_id
item_category
label_buy_7d
```

避免把 ID、日期、标签错误放入模型。

### 7.2 使用 float32 降低内存

特征列会转为 `float32`，减少内存占用。

空间占用从近似：

```text
O(n * d * 8)
```

降低到约：

```text
O(n * d * 4)
```

### 7.3 使用 SGD 逻辑回归

模型使用：

```python
SGDClassifier(loss="log_loss")
```

它每轮训练只需要线性扫描样本，训练复杂度为：

```text
O(T * n * d)
```

相比一些更重的优化器，更适合较大的特征宽表。

### 7.4 Top 比例评估使用 nlargest

原始完整排序：

```text
O(m log m)
```

优化为 TopK 选择：

```text
O(m log k)
```

因为业务上只关心预测概率最高的前 5%、10%、20% 样本。

### 7.5 特征重要性使用 nlargest

只输出前 N 个重要特征，不对全部特征完整排序。

复杂度从：

```text
O(d log d)
```

优化为：

```text
O(d log N)
```

## 8. 总体时间复杂度

主要步骤如下：

| 步骤 | 时间复杂度 |
|---|---|
| 读取数据 | `O(n * d)` |
| 特征数值转换 | `O(n * d)` |
| 缺失值填充 | `O(n * d)` |
| 标准化 | `O(n * d)` |
| SGD 逻辑回归训练 | `O(T * n * d)` |
| 预测概率 | `O(m * d)` |
| AUC / PR-AUC | `O(m log m)` |
| Top 比例评估 | `O(m log k)` |

因此，训练阶段主要复杂度为：

```text
O(T * n * d)
```

评估阶段如果保留精确 AUC / PR-AUC，会包含：

```text
O(m log m)
```

这是因为 AUC 和 PR-AUC 本身需要按预测概率进行排序。

## 9. 空间复杂度

主要空间来自特征矩阵：

```text
O(n * d)
```

使用 `float32` 后可以降低实际内存占用。

模型参数本身只需要保存每个特征的系数：

```text
O(d)
```

## 10. 输出结果

程序会输出：

| 文件 | 说明 |
|---|---|
| `purchase_probability_model.joblib` | 训练好的模型 |
| `model_metrics.csv` | AUC、PR-AUC 等指标 |
| `top_rate_metrics.csv` | Top5%、Top10%、Top20% 命中效果 |
| `feature_importance.csv` | 逻辑回归特征重要性 |
| `purchase_probability_predictions.csv` | 验证集和测试集预测概率 |

## 11. 运行方式

进入项目文件夹后运行：

```bash
python run_purchase_model.py
```

运行成功后，会在配置文件指定的输出文件夹中生成模型和结果。
