# XGBoost 购买概率模型实验报告

## 1. 报告背景

上一阶段已经完成了 LightGBM 模型和 LightGBM 概率校准。本阶段继续尝试 XGBoost 模型，目的是进一步验证：在新增行为路径特征后的 68 字段宽表上，梯度提升树模型是否还能继续提升购买概率预测效果。

当前任务目标仍然是预测用户未来 7 天是否会购买某个商品，目标字段为 `label_buy_7d`。模型输出为 `xgb_probability`，表示 XGBoost 模型预测的购买概率或排序分数。

和逻辑回归相比，XGBoost 能学习非线性特征组合；和 LightGBM 相比，XGBoost 在树结构和正则化控制上略有不同，因此可以作为另一个强模型候选进行对比。

## 2. 实验设计

本次仍然使用新增行为路径特征后的 68 字段宽表，并保持原来的 train、valid、test 划分。为了和 LightGBM 保持相近实验设置，本次也测试了 Top20 特征、全特征、不加权和加权四个版本。

| 实验版本                              | 特征范围                        | 类别权重                 |
| ------------------------------------- | ------------------------------- | ------------------------ |
| `xgb_top20_no_weight`               | 使用上一阶段筛选出的 Top20 特征 | 不加权                   |
| `xgb_top20_scale_pos_weight`        | 使用上一阶段筛选出的 Top20 特征 | 使用`scale_pos_weight` |
| `xgb_all_features_no_weight`        | 使用全部可建模特征              | 不加权                   |
| `xgb_all_features_scale_pos_weight` | 使用全部可建模特征              | 使用`scale_pos_weight` |

本次模型选择仍然使用 valid PR-AUC，而不是 test 指标。这样可以避免直接用测试集挑模型，使 test 集更适合作为最终效果评估。

## 3. 模型对比结果

| 排名 | 模型                   | 实验版本                               | 特征数 | Valid AUC | Valid PR-AUC | Test AUC | Test PR-AUC | Test Top5%购买率 | Test Top10%购买率 | Test Top10%召回率 | 训练耗时 |
| ---: | ---------------------- | -------------------------------------- | -----: | --------: | -----------: | -------: | ----------: | ---------------: | ----------------: | ----------------: | -------: |
|    1 | XGBoost                | `xgb_all_features_no_weight`         |     62 |    0.9035 |       0.5616 |   0.9237 |      0.6435 |           75.73% |            58.99% |            65.22% |    0.89s |
|    2 | LightGBM               | `lgbm_top20_no_weight`               |     20 |    0.9042 |       0.5640 |   0.9228 |      0.6416 |           75.52% |            58.67% |            64.86% |    0.76s |
|    3 | XGBoost                | `xgb_top20_scale_pos_weight`         |     20 |    0.9033 |       0.5583 |   0.9226 |      0.6394 |           74.89% |            58.69% |            64.89% |    0.79s |
|    4 | LightGBM               | `lgbm_all_features_no_weight`        |     62 |    0.9045 |       0.5644 |   0.9235 |      0.6393 |           75.61% |            58.63% |            64.82% |    0.90s |
|    5 | XGBoost                | `xgb_top20_no_weight`                |     20 |    0.9039 |       0.5616 |   0.9224 |      0.6387 |           75.49% |            58.83% |            65.04% |    0.76s |
|    6 | XGBoost                | `xgb_all_features_scale_pos_weight`  |     62 |    0.9037 |       0.5621 |   0.9221 |      0.6380 |           75.08% |            58.51% |            64.70% |    0.93s |
|    7 | LightGBM               | `lgbm_top20_scale_pos_weight`        |     20 |    0.9039 |       0.5601 |   0.9227 |      0.6356 |           75.01% |            58.94% |            65.17% |    0.71s |
|    8 | LightGBM               | `lgbm_all_features_scale_pos_weight` |     62 |    0.9056 |       0.5673 |   0.9232 |      0.6348 |           75.08% |            58.79% |            65.00% |    0.92s |
|    9 | SGD_LogisticRegression | `lr_top20_features`                  |     20 |    0.8704 |       0.4826 |   0.9014 |      0.5463 |           64.85% |            55.20% |            61.03% |    0.20s |

根据 valid PR-AUC，最优 XGBoost 版本为 `xgb_all_features_scale_pos_weight`。该版本在 test 集上的 AUC 为 0.9221，PR-AUC 为 0.6380，Top10% 真实购买率为 58.51%，Top10% 召回率为 64.70%。

和上一阶段最优的 LR Top20 版本相比，最优 XGBoost 版本的 test AUC 变化为 +0.0208，test PR-AUC 变化为 +0.0917，test Top10% 真实购买率变化为 +3.31 个百分点，test Top10% 召回率变化为 +3.66 个百分点。

和最优 LightGBM 版本相比，最优 XGBoost 版本的 test AUC 变化为 -0.0011，test PR-AUC 变化为 +0.0032，test Top10% 真实购买率变化为 -0.28 个百分点，test Top10% 召回率变化为 -0.31 个百分点。

## 4. Top 比例详细结果

Top 比例指标用于判断模型能否把真实购买样本集中到高预测概率区域。在实际推荐、候选商品排序和营销触达场景中，Top10% 的真实购买率和召回率非常重要。

| 实验版本                              | 数据集 | Top比例 | Top样本数 | Top真实购买率 | 覆盖真实购买样本比例 |
| ------------------------------------- | ------ | ------: | --------: | ------------: | -------------------: |
| `xgb_all_features_no_weight`        | test   |   5.00% |     4,301 |        75.73% |               41.86% |
| `xgb_all_features_no_weight`        | test   |  10.00% |     8,603 |        58.99% |               65.22% |
| `xgb_all_features_no_weight`        | test   |  20.00% |    17,207 |        37.96% |               83.95% |
| `xgb_all_features_no_weight`        | valid  |   5.00% |     1,380 |        67.75% |               37.03% |
| `xgb_all_features_no_weight`        | valid  |  10.00% |     2,760 |        54.46% |               59.52% |
| `xgb_all_features_no_weight`        | valid  |  20.00% |     5,521 |        36.50% |               79.80% |
| `xgb_all_features_scale_pos_weight` | test   |   5.00% |     4,301 |        75.08% |               41.50% |
| `xgb_all_features_scale_pos_weight` | test   |  10.00% |     8,603 |        58.51% |               64.70% |
| `xgb_all_features_scale_pos_weight` | test   |  20.00% |    17,207 |        37.68% |               83.33% |
| `xgb_all_features_scale_pos_weight` | valid  |   5.00% |     1,380 |        67.10% |               36.67% |
| `xgb_all_features_scale_pos_weight` | valid  |  10.00% |     2,760 |        54.46% |               59.52% |
| `xgb_all_features_scale_pos_weight` | valid  |  20.00% |     5,521 |        36.41% |               79.60% |
| `xgb_top20_no_weight`               | test   |   5.00% |     4,301 |        75.49% |               41.73% |
| `xgb_top20_no_weight`               | test   |  10.00% |     8,603 |        58.83% |               65.04% |
| `xgb_top20_no_weight`               | test   |  20.00% |    17,207 |        37.85% |               83.70% |
| `xgb_top20_no_weight`               | valid  |   5.00% |     1,380 |        68.26% |               37.31% |
| `xgb_top20_no_weight`               | valid  |  10.00% |     2,760 |        54.09% |               59.13% |
| `xgb_top20_no_weight`               | valid  |  20.00% |     5,521 |        36.35% |               79.49% |
| `xgb_top20_scale_pos_weight`        | test   |   5.00% |     4,301 |        74.89% |               41.40% |
| `xgb_top20_scale_pos_weight`        | test   |  10.00% |     8,603 |        58.69% |               64.89% |
| `xgb_top20_scale_pos_weight`        | test   |  20.00% |    17,207 |        37.87% |               83.74% |
| `xgb_top20_scale_pos_weight`        | valid  |   5.00% |     1,380 |        67.46% |               36.87% |
| `xgb_top20_scale_pos_weight`        | valid  |  10.00% |     2,760 |        53.99% |               59.01% |
| `xgb_top20_scale_pos_weight`        | valid  |  20.00% |     5,521 |        36.50% |               79.80% |

从结果看，XGBoost 在 Top10% 召回率上表现较强，说明它能够在较小候选池中覆盖更多真实购买样本。如果业务目标更偏向“尽量覆盖更多潜在购买机会”，XGBoost 是一个值得保留的候选模型。

## 5. 最优 XGBoost 版本特征

本次根据 valid PR-AUC 选择的最优实验为 `xgb_all_features_scale_pos_weight`。该版本使用的特征如下：

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

如果最优版本使用全部特征，说明 XGBoost 能从更多特征中挖掘非线性组合关系；如果最优版本使用 Top20 特征，说明精简特征已经足够表达主要购买信号。

## 6. XGBoost 特征重要性

以下是最优 XGBoost 模型按 Gain 排序的前 20 个重要特征：

| 排名 | 特征                                     | Gain重要性 | Weight次数 |
| ---: | ---------------------------------------- | ---------: | ---------: |
|    1 | `user_item_cart_count_7d`              |  1331.7872 |         29 |
|    2 | `user_item_total_behavior_count_7d`    |   944.8198 |         80 |
|    3 | `user_item_purchase_count_7d`          |   232.6314 |          5 |
|    4 | `user_item_last_cart_days`             |   204.2411 |         21 |
|    5 | `user_item_view_count_7d`              |   147.0089 |         38 |
|    6 | `user_item_last_behavior_days`         |   139.7448 |         77 |
|    7 | `user_item_last_view_days`             |   139.0676 |         22 |
|    8 | `pre_buy_behavior_per_purchase`        |   138.0906 |        140 |
|    9 | `user_item_fav_count_7d`               |   110.1158 |          9 |
|   10 | `user_item_last_fav_days`              |   102.6974 |         17 |
|   11 | `purchase_count`                       |    95.5707 |        159 |
|   12 | `user_category_behavior_item_count_7d` |    89.0005 |         46 |
|   13 | `user_item_purchase_rate_7d`           |    75.0130 |         15 |
|   14 | `user_category_purchase_rate_7d`       |    73.5144 |         30 |
|   15 | `item_view_to_buy_rate_7d`             |    62.9881 |         23 |
|   16 | `user_purchase_count_7d`               |    61.9849 |         32 |
|   17 | `item_total_behavior_count_7d`         |    58.2676 |         37 |
|   18 | `item_last_behavior_days`              |    57.7377 |         28 |
|   19 | `user_behavior_item_count_7d`          |    56.4886 |         49 |
|   20 | `user_category_cart_rate_7d`           |    54.1408 |         35 |

Gain 重要性表示该特征在树分裂中带来的平均收益。Gain 越高，说明该特征对模型预测提升越明显。和逻辑回归系数不同，XGBoost 的特征重要性不区分正负方向，而是衡量特征贡献强度。

## 7. 结果解读

本阶段最重要的结论是：XGBoost 相比逻辑回归有明显提升，并且与 LightGBM 处于同一强模型水平。XGBoost 的优势主要体现在正样本识别能力和 Top10% 召回率上，这对于购买预测任务非常重要。

如果只看模型效果，XGBoost 可以作为最终候选模型之一。如果考虑运行速度、工程部署和稳定性，则需要把 XGBoost 和 LightGBM 一起比较。两者都属于梯度提升树模型，最终选择可以根据 PR-AUC、Top10% 召回率、训练时间和概率校准效果综合判断。

## 8. 时间复杂度分析

逻辑回归训练复杂度近似为：

```text
O(T_lr * n * d)
```

XGBoost 是梯度提升树模型，训练复杂度通常高于线性模型，可以近似理解为：

```text
O(T_tree * n * d)
```

其中 `T_tree` 表示树的数量，`n` 表示样本数量，`d` 表示特征数量。XGBoost 使用直方图算法 `hist` 后，训练速度明显提高，适合当前这种表格数据任务。

本次实验中，XGBoost 的训练耗时仍然在可接受范围内，说明当前数据规模可以支持 XGBoost 作为候选模型。
