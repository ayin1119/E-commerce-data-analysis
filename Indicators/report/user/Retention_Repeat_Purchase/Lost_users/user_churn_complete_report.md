# 流失用户分析

## 1. 报告背景

本报告围绕“流失用户分析”进行代码规范化修改与时间复杂度优化说明。该分析的目标是根据用户距离最近一次购买的时间，识别可能已经流失或存在流失风险的用户。

原始逻辑主要依据 `days_since_last_purchase` 和 `hours_since_last_purchase` 两个字段判断用户距离上一次购买的时间。距离上次购买时间越长，用户流失风险越高。原始 notebook 中通常通过完整排序的方式，将距离最近一次购买时间最长的前 20% 用户标记为“流失用户”，将前 20% 到前 50% 的用户标记为“有流失倾向用户”。

## 2. 修改目标

| 修改目标       | 说明                                                           |
| -------------- | -------------------------------------------------------------- |
| 配置参数文件   | 将输入路径、输出路径、字段名、流失比例等参数放入`config.py`  |
| 接口定义       | 定义统一接口`run_user_churn_analysis(config)`                |
| 代码封装       | 将读取、检查、清洗、阈值计算、标签生成、保存结果拆分为独立函数 |
| 时间复杂度优化 | 默认使用分位数阈值分层，避免完整排序                           |
| 可选排名       | 如果需要保留精确排名，可通过`keep_rank=True` 开启排序        |
| 可维护性优化   | 后续修改路径、比例、输出文件名时只需要修改配置文件             |

## 3. 修改后的项目结构

修改后的项目建议拆分为三个 Python 文件：

```text
user_churn_project/
│
├── config.py
├── user_churn_pipeline.py
└── run_user_churn.py
```

三个文件的职责如下：

| 文件                       | 作用                                                                                   |
| -------------------------- | -------------------------------------------------------------------------------------- |
| `config.py`              | 配置参数文件，保存输入路径、输出路径、字段名、流失比例、是否保留排名等参数             |
| `user_churn_pipeline.py` | 核心代码封装文件，包含数据读取、字段检查、数据清洗、阈值计算、标签生成和保存结果等函数 |
| `run_user_churn.py`      | 运行入口文件，负责导入配置并调用统一接口运行程序                                       |

这种拆分方式使项目结构更清晰。修改参数时只改 `config.py`，查看核心逻辑时只看 `user_churn_pipeline.py`，运行程序时只执行 `run_user_churn.py`。

## 4. 修改后的业务流程

修改后的程序整体流程如下：

```text
读取配置参数
      ↓
读取最近一次购买间隔表
      ↓
检查 user_id、days_since_last_purchase、hours_since_last_purchase 是否存在
      ↓
将 days_since_last_purchase、hours_since_last_purchase 转为数值
      ↓
去掉无法计算的用户
      ↓
计算流失用户阈值和流失倾向用户阈值
      ↓
根据阈值直接生成 churn_label
      ↓
根据 keep_rank 判断是否生成完整排名
      ↓
保存结果 CSV
```

## 5. 输出结果字段说明

最终输出文件名为：

```text
user_churn_result.csv
```

输出字段如下：

| 字段                          | 含义                         |
| ----------------------------- | ---------------------------- |
| `user_id`                   | 用户编号                     |
| `days_since_last_purchase`  | 距离最近一次购买过去的天数   |
| `hours_since_last_purchase` | 距离最近一次购买过去的小时数 |
| `churn_threshold`           | 流失用户阈值                 |
| `risk_threshold`            | 流失倾向用户阈值             |
| `churn_label`               | 用户流失标签                 |

如果配置中设置：

```python
"keep_rank": True
```

还会额外输出：

| 字段          | 含义             |
| ------------- | ---------------- |
| `user_rank` | 用户流失风险排名 |
| `rank_rate` | 用户排名比例     |

## 6. 时间复杂度符号定义

为了分析时间复杂度，先定义以下符号：

```text
n：有效用户数量，即有 days_since_last_purchase 的用户数量
```

其中，`n` 是清洗后参与流失判断的用户数量。

## 7. 原始时间复杂度分析

原始做法通常是：

```text
读取最近一次购买间隔表
清洗数据
按照 days_since_last_purchase、hours_since_last_purchase 和 user_id 对全部用户完整排序
生成 user_rank
计算 rank_rate
根据 rank_rate 给用户打标签
保存结果
```

各步骤时间复杂度如下：

| 步骤     | 时间复杂度     | 说明                     |
| -------- | -------------- | ------------------------ |
| 读取数据 | `O(n)`       | 需要读取用户记录         |
| 数据清洗 | `O(n)`       | 转换数值字段并去除缺失值 |
| 完整排序 | `O(n log n)` | 对全部用户按流失风险排序 |
| 生成排名 | `O(n)`       | 为每个用户生成排名       |
| 生成标签 | `O(n)`       | 根据排名比例判断用户类别 |
| 保存结果 | `O(n)`       | 将结果写出               |

因此，原始整体时间复杂度为：

```text
O(n log n)
```

其中最主要的耗时来自完整排序。

## 8. 时间复杂度优化方案

本次优化的核心是：默认不再对所有用户做完整排序，而是使用分位数阈值直接分层。

原始做法是：

```text
完整排序全部用户
根据排名前 20%、前 50% 判断用户类型
```

优化后做法是：

```text
计算 days_since_last_purchase 的 80% 分位数和 50% 分位数
days_since_last_purchase 大于等于 80% 分位数 → 流失用户
days_since_last_purchase 大于等于 50% 分位数 → 有流失倾向用户
其余 → 普通用户
```

核心代码为：

```python
churn_quantile = 1 - churn_ratio
risk_quantile = 1 - risk_ratio

churn_threshold = cleaned_df[days_col].quantile(churn_quantile)
risk_threshold = cleaned_df[days_col].quantile(risk_quantile)
```

然后使用：

```python
result["churn_label"] = np.select(
    [
        result[days_col] >= churn_threshold,
        result[days_col] >= risk_threshold
    ],
    [
        "流失用户",
        "有流失倾向用户"
    ],
    default="普通用户"
)
```

直接生成标签。

这样避免了完整排序，主流程复杂度更接近 `O(n)`。

## 9. 优化后的时间复杂度分析

优化后默认 `keep_rank = False`，主要步骤如下：

| 步骤           | 时间复杂度   | 说明                       |
| -------------- | ------------ | -------------------------- |
| 读取数据       | `O(n)`     | 读取用户最近一次购买间隔表 |
| 检查字段       | `O(1)`     | 字段数量固定               |
| 数据清洗       | `O(n)`     | 数值转换和缺失值处理       |
| 计算分位数阈值 | 近似`O(n)` | 用分位数直接得到分层阈值   |
| 生成流失标签   | `O(n)`     | 每个用户判断一次           |
| 保存结果       | `O(n)`     | 将结果写出                 |

因此，优化后的默认时间复杂度为：

```text
O(n)
```

如果配置中设置：

```python
"keep_rank": True
```

则会执行完整排序：

```python
result = result.sort_values(
    by=[days_col, hours_col, user_col],
    ascending=[False, False, True]
)
```

此时排序复杂度为：

```text
O(n log n)
```

整体复杂度会回到：

```text
O(n log n)
```

因此，本项目默认推荐：

```python
"keep_rank": False
```

这样可以保留时间复杂度优化效果。

## 10. 空间复杂度分析

程序需要保存用户表、清洗后的数据和结果表，因此空间复杂度为：

```text
O(n)
```

如果不保留完整排序排名，空间占用不会显著增加。如果设置 `keep_rank = True`，仍然主要保存同一张用户结果表，空间复杂度依然可以看作 `O(n)`。

## 11. 优化前后对比

| 对比项     | 优化前                                 | 优化后                                  | 优化效果           |
| ---------- | -------------------------------------- | --------------------------------------- | ------------------ |
| 参数管理   | 路径、字段名、比例直接写在 notebook 中 | 使用`config.py` 统一管理              | 修改更方便         |
| 代码结构   | 所有逻辑集中在 notebook 中             | 拆分为配置、核心封装、运行入口          | 可读性提升         |
| 接口设计   | 没有统一主接口                         | 使用`run_user_churn_analysis(config)` | 调用更简单         |
| 分层方法   | 完整排序后按排名比例分层               | 默认使用分位数阈值分层                  | 降低时间复杂度     |
| 排名字段   | 默认生成完整排名                       | 通过`keep_rank` 控制是否生成          | 兼顾效率和业务需求 |
| 时间复杂度 | `O(n log n)`                         | 默认`O(n)`                            | 明显降低           |
| 空间复杂度 | `O(n)`                               | `O(n)`                                | 基本不变           |

## 12. 最终结论

本次修改完成了流失用户分析代码的配置参数文件设计、接口定义、代码封装和时间复杂度优化。

在配置参数方面，使用 `config.py` 集中管理输入路径、输出路径、字段名、流失比例、流失倾向比例、是否保留排名和输出文件名。这样后续修改路径或分层比例时，不需要改动核心代码。

在代码封装方面，将完整分析流程拆分为 `load_user_purchase_interval()`、`check_required_columns()`、`clean_user_purchase_interval()`、`calculate_churn_thresholds()`、`add_churn_labels_by_threshold()`、`add_rank_if_needed()`、`save_result()` 和 `run_user_churn_analysis()` 等函数。每个函数只负责一个步骤，代码结构更加清晰。

在接口定义方面，使用 `run_user_churn_analysis(config)` 作为统一接口。外部运行文件只需要导入配置并调用该函数，即可完成完整分析流程。

在时间复杂度方面，原始做法需要对所有用户进行完整排序，整体复杂度为：

```text
O(n log n)
```

优化后默认使用分位数阈值进行流失标签划分，不再进行完整排序，整体复杂度降低为：

```text
O(n)
```

如果业务需要保留严格排名，可以将 `keep_rank` 设置为 `True`，但复杂度会回到 `O(n log n)`。因此，本次修改在保留业务可选性的同时，实现了默认情况下的时间复杂度优化。
