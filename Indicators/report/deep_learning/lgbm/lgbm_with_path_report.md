# LightGBM 购买概率模型实验报告

## 1. 报告背景

因此，本阶段继续做模型能力提升，尝试用 LightGBM 替代原来的 SGD 逻辑回归模型。

原来的 SGD 逻辑回归属于线性模型，主要学习单个特征与购买概率之间的线性关系。LightGBM 属于梯度提升树模型，可以学习更复杂的非线性组合关系，例如“用户对该商品有浏览、该商品转化率较高、用户历史购买路径较短”这类组合信号。因此，本阶段的核心目标是判断 LightGBM 是否能够进一步提高购买预测效果。

## 2. 实验设计

本次实验仍然使用新增行为路径特征后的 68 字段宽表，目标字段仍为 `label_buy_7d`。为了便于和前面的结果对比，仍然使用原来的 train、valid、test 划分。

本次设计了 4 个 LightGBM 实验版本：

| 实验版本                               | 特征范围                        | 类别权重                 |
| -------------------------------------- | ------------------------------- | ------------------------ |
| `lgbm_top20_no_weight`               | 使用上一阶段筛选出的 Top20 特征 | 不加权                   |
| `lgbm_top20_scale_pos_weight`        | 使用上一阶段筛选出的 Top20 特征 | 使用`scale_pos_weight` |
| `lgbm_all_features_no_weight`        | 使用全部可建模特征              | 不加权                   |
| `lgbm_all_features_scale_pos_weight` | 使用全部可建模特征              | 使用`scale_pos_weight` |

其中，`scale_pos_weight` 是根据训练集负样本数和正样本数的比例设置的，用于增强模型对正样本的关注。

本次模型选择标准是 valid PR-AUC，而不是 test 指标。这样做是为了避免用测试集挑模型，保证测试集仍然用于最终效果评估。

## 3. 模型对比结果

| 排名 | 模型                   | 实验版本                               | 特征数 | Valid AUC | Valid PR-AUC | Test AUC | Test PR-AUC | Test Top5%购买率 | Test Top10%购买率 | Test Top10%召回率 | 训练耗时 |
| ---: | ---------------------- | -------------------------------------- | -----: | --------: | -----------: | -------: | ----------: | ---------------: | ----------------: | ----------------: | -------: |
|    1 | LightGBM               | `lgbm_top20_no_weight`               |     20 |    0.9042 |       0.5640 |   0.9228 |      0.6416 |           75.52% |            58.67% |            64.86% |    0.76s |
|    2 | LightGBM               | `lgbm_all_features_no_weight`        |     62 |    0.9045 |       0.5644 |   0.9235 |      0.6393 |           75.61% |            58.63% |            64.82% |    0.90s |
|    3 | LightGBM               | `lgbm_top20_scale_pos_weight`        |     20 |    0.9039 |       0.5601 |   0.9227 |      0.6356 |           75.01% |            58.94% |            65.17% |    0.71s |
|    4 | LightGBM               | `lgbm_all_features_scale_pos_weight` |     62 |    0.9056 |       0.5673 |   0.9232 |      0.6348 |           75.08% |            58.79% |            65.00% |    0.92s |
|    5 | SGD_LogisticRegression | `lr_top20_features`                  |     20 |    0.8704 |       0.4826 |   0.9014 |      0.5463 |           64.85% |            55.20% |            61.03% |    0.20s |

根据 valid PR-AUC，最优 LightGBM 版本为 `lgbm_all_features_scale_pos_weight`。该版本在 test 集上的 AUC 为 0.9232，PR-AUC 为 0.6348，Top10% 真实购买率为 58.79%，Top10% 召回率为 65.00%。

和上一阶段最优的 LR Top20 版本相比，最优 LightGBM 版本的 test AUC 变化为 +0.0218，test PR-AUC 变化为 +0.0885，test Top5% 真实购买率变化为 +10.23 个百分点，test Top10% 真实购买率变化为 +3.59 个百分点，test Top10% 召回率变化为 +3.97 个百分点。

## 4. Top 比例详细结果

Top 比例指标用于判断模型能否把真实购买样本集中到高预测概率区域。对于推荐排序、营销触达和候选商品筛选任务，Top5%、Top10%、Top20% 的真实购买率和召回率比单纯 AUC 更有业务意义。

| 实验版本                               | 数据集 | Top比例 | Top样本数 | Top真实购买率 | 覆盖真实购买样本比例 |
| -------------------------------------- | ------ | ------: | --------: | ------------: | -------------------: |
| `lgbm_all_features_no_weight`        | test   |   5.00% |     4,301 |        75.61% |               41.79% |
| `lgbm_all_features_no_weight`        | test   |  10.00% |     8,603 |        58.63% |               64.82% |
| `lgbm_all_features_no_weight`        | test   |  20.00% |    17,207 |        37.91% |               83.83% |
| `lgbm_all_features_no_weight`        | valid  |   5.00% |     1,380 |        67.46% |               36.87% |
| `lgbm_all_features_no_weight`        | valid  |  10.00% |     2,760 |        54.35% |               59.41% |
| `lgbm_all_features_no_weight`        | valid  |  20.00% |     5,521 |        36.48% |               79.76% |
| `lgbm_all_features_scale_pos_weight` | test   |   5.00% |     4,301 |        75.08% |               41.50% |
| `lgbm_all_features_scale_pos_weight` | test   |  10.00% |     8,603 |        58.79% |               65.00% |
| `lgbm_all_features_scale_pos_weight` | test   |  20.00% |    17,207 |        37.85% |               83.70% |
| `lgbm_all_features_scale_pos_weight` | valid  |   5.00% |     1,380 |        67.75% |               37.03% |
| `lgbm_all_features_scale_pos_weight` | valid  |  10.00% |     2,760 |        54.75% |               59.84% |
| `lgbm_all_features_scale_pos_weight` | valid  |  20.00% |     5,521 |        36.41% |               79.60% |
| `lgbm_top20_no_weight`               | test   |   5.00% |     4,301 |        75.52% |               41.74% |
| `lgbm_top20_no_weight`               | test   |  10.00% |     8,603 |        58.67% |               64.86% |
| `lgbm_top20_no_weight`               | test   |  20.00% |    17,207 |        37.91% |               83.83% |
| `lgbm_top20_no_weight`               | valid  |   5.00% |     1,380 |        67.54% |               36.91% |
| `lgbm_top20_no_weight`               | valid  |  10.00% |     2,760 |        54.38% |               59.45% |
| `lgbm_top20_no_weight`               | valid  |  20.00% |     5,521 |        36.41% |               79.60% |
| `lgbm_top20_scale_pos_weight`        | test   |   5.00% |     4,301 |        75.01% |               41.46% |
| `lgbm_top20_scale_pos_weight`        | test   |  10.00% |     8,603 |        58.94% |               65.17% |
| `lgbm_top20_scale_pos_weight`        | test   |  20.00% |    17,207 |        37.80% |               83.59% |
| `lgbm_top20_scale_pos_weight`        | valid  |   5.00% |     1,380 |        67.39% |               36.83% |
| `lgbm_top20_scale_pos_weight`        | valid  |  10.00% |     2,760 |        54.35% |               59.41% |
| `lgbm_top20_scale_pos_weight`        | valid  |  20.00% |     5,521 |        36.24% |               79.25% |

从结果看，LightGBM 相比逻辑回归的主要提升体现在 PR-AUC 和召回能力上。也就是说，LightGBM 更擅长把真实购买样本集中到高分区域，尤其是在 Top10% 样本中覆盖了更多真实购买用户-商品组合。

## 5. 最优 LightGBM 版本特征

本次根据 valid PR-AUC 选择的最优实验为 `lgbm_all_features_scale_pos_weight`。该版本使用的特征如下：

```text
1. `user_item_total_behavior_count_7d`
2. `user_item_view_count_7d`
3. `user_item_fav_count_7d`
4. `user_item_cart_count_7d`
5. `user_item_purchase_count_7d`
6. `user_item_active_days_7d`
7. `user_item_last_behavior_days`
8. `user_item_last_view_days`
9. `user_item_last_fav_days`
10. `user_item_last_cart_days`
11. `user_item_last_purchase_days`
12. `user_item_has_view`
13. `user_item_has_fav`
14. `user_item_has_cart`
15. `user_item_has_purchase`
16. `user_item_cart_rate_7d`
17. `user_item_purchase_rate_7d`
18. `user_total_behavior_count_7d`
19. `user_view_count_7d`
20. `user_fav_count_7d`
21. `user_cart_count_7d`
22. `user_purchase_count_7d`
23. `user_active_days_7d`
24. `user_behavior_item_count_7d`
25. `user_behavior_category_count_7d`
26. `user_purchase_item_count_7d`
27. `user_purchase_category_count_7d`
28. `user_purchase_rate_7d`
29. `user_cart_rate_7d`
30. `user_last_behavior_days`
31. `user_last_purchase_days`
32. `item_total_behavior_count_7d`
33. `item_view_count_7d`
34. `item_fav_count_7d`
35. `item_cart_count_7d`
36. `item_purchase_count_7d`
37. `item_behavior_user_count_7d`
38. `item_purchase_user_count_7d`
39. `item_active_days_7d`
40. `item_view_to_fav_rate_7d`
41. `item_fav_to_cart_rate_7d`
42. `item_cart_to_buy_rate_7d`
43. `item_view_to_buy_rate_7d`
44. `item_last_behavior_days`
45. `item_last_purchase_days`
46. `user_category_total_behavior_count_7d`
47. `user_category_view_count_7d`
48. `user_category_fav_count_7d`
49. `user_category_cart_count_7d`
50. `user_category_purchase_count_7d`
51. `user_category_active_days_7d`
52. `user_category_behavior_item_count_7d`
53. `user_category_purchase_item_count_7d`
54. `user_category_purchase_rate_7d`
55. `user_category_cart_rate_7d`
56. `user_category_behavior_share_7d`
57. `user_category_purchase_share_7d`
58. `user_category_last_behavior_days`
59. `user_category_last_purchase_days`
60. `pre_buy_behavior_count`
61. `purchase_count`
62. `pre_buy_behavior_per_purchase`
```

如果最优版本使用全部特征，说明虽然 Top20 在线性模型中效果最好，但树模型能够从更多特征中学习到额外的非线性信息。如果最优版本使用 Top20 特征，则说明低重要性特征对树模型帮助也有限，可以继续使用精简版本。

## 6. LightGBM 特征重要性

以下是最优 LightGBM 模型按 Gain 排序的前 20 个重要特征：

| 排名 | 特征                                     | Gain重要性 | Split次数 |
| ---: | ---------------------------------------- | ---------: | --------: |
|    1 | `user_item_cart_count_7d`              |   48857.15 |        29 |
|    2 | `user_item_total_behavior_count_7d`    |   43640.87 |        95 |
|    3 | `user_item_view_count_7d`              |   28020.21 |        33 |
|    4 | `pre_buy_behavior_per_purchase`        |   26486.89 |       144 |
|    5 | `user_item_last_cart_days`             |   20176.55 |        38 |
|    6 | `purchase_count`                       |   17819.11 |       189 |
|    7 | `user_item_last_behavior_days`         |   11315.12 |        77 |
|    8 | `pre_buy_behavior_count`               |    8593.55 |        92 |
|    9 | `user_category_behavior_item_count_7d` |    5855.45 |        75 |
|   10 | `user_behavior_category_count_7d`      |    4102.66 |        95 |
|   11 | `user_category_purchase_rate_7d`       |    3838.51 |        30 |
|   12 | `user_item_last_fav_days`              |    3731.73 |        25 |
|   13 | `user_cart_count_7d`                   |    3455.80 |        68 |
|   14 | `user_cart_rate_7d`                    |    3265.28 |        83 |
|   15 | `item_last_behavior_days`              |    3201.53 |        45 |
|   16 | `user_behavior_item_count_7d`          |    3150.66 |        55 |
|   17 | `user_category_cart_rate_7d`           |    2905.27 |        53 |
|   18 | `user_category_last_behavior_days`     |    2826.31 |        35 |
|   19 | `user_total_behavior_count_7d`         |    2804.83 |        39 |
|   20 | `user_fav_count_7d`                    |    2491.39 |        66 |

Gain 重要性表示某个特征在树分裂过程中带来的损失下降贡献。Gain 越高，说明该特征对模型提升越明显。和逻辑回归系数不同，LightGBM 的特征重要性不区分正向和负向，而是衡量该特征对模型预测的整体贡献。

## 7. 结果解读

LightGBM 在当前任务中确实带来了提升，尤其是 PR-AUC 和 Top10% 召回率。PR-AUC 更关注正样本识别能力，而购买行为预测本身就是一个正样本较少的问题，因此 PR-AUC 的提升比单纯 AUC 的小幅变化更有意义。

从业务角度看，Top10% 召回率提升说明模型能在较小的候选池中覆盖更多真实购买样本。如果用于推荐或营销触达，这意味着同样触达 10% 的用户-商品组合，LightGBM 能覆盖更多真实购买机会。

## 8. 时间复杂度分析

逻辑回归训练复杂度近似为：

```text
O(T_lr * n * d)
```

LightGBM 是基于梯度提升树的模型，训练复杂度通常高于线性模型。可以近似理解为：

```text
O(T_tree * n * d)
```

其中 `T_tree` 是树的数量，`n` 是样本数，`d` 是特征数。LightGBM 通过直方图分桶、特征采样和叶子优先生长降低计算成本，但整体训练成本仍然高于线性模型。

本次数据规模不大，因此 LightGBM 训练耗时仍然可接受。后续如果使用原始比例大宽表，需要重点关注训练时间和内存占用。