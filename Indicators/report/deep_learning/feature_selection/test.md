# 特征筛选实验模块测试文档

## 1. 文档说明

本文档用于测试“68 字段购买概率模型的特征筛选实验模块”。该模块的目标是比较不同特征数量下模型效果是否稳定，判断是否可以在减少特征数量的同时保持接近甚至更好的预测效果。

本次测试文档基于当前上传的配置文件、特征筛选实验代码、README 说明和运行入口脚本编写。由于本次没有上传真实特征宽表、特征重要性结果文件和实验输出 CSV，因此本文档主要进行静态代码检查、配置检查和流程测试设计。真实的 AUC、PR-AUC、Top10% 购买率、训练耗时和最优模型结果需要在本地运行实验后补充。

## 2. 测试对象

| 文件类型         | 文件名                             | 是否存在   | 文件大小    |
|:-----------------|:-----------------------------------|:-----------|:------------|
| 配置文件         | config_feature_selection(2).py     | 是         | 963 bytes   |
| 特征筛选实验代码 | feature_selection_experiment(2).py | 是         | 8,294 bytes |
| 实验说明文档     | README_特征筛选实验说明(2).md      | 是         | 672 bytes   |
| 运行入口脚本     | run_feature_selection(2).py        | 是         | 428 bytes   |

## 3. 模块背景

购买概率模型原本可以使用全部可建模特征进行训练，但全部特征并不一定都对模型有正向贡献。部分低重要性特征可能会增加训练成本，也可能带来噪声。因此，本模块基于已有的特征重要性排序，构造多个特征子集进行对比，包括：

```text
全部特征
Top50 特征
Top40 特征
Top30 特征
Top20 特征
```

通过比较各版本在 valid/test 上的 AUC、PR-AUC、Top 比例命中效果和训练耗时，可以判断精简特征后模型是否仍然稳定。

## 4. 测试目标

本次测试主要验证以下目标：

第一，检查配置文件是否正确设置输入文件、输出目录、数据集划分字段、目标字段、非建模字段、特征筛选版本、模型参数和 Top 比例。

第二，检查代码是否能够基于特征重要性排序构造 all_features、top50_features、top40_features、top30_features 和 top20_features 五个实验版本。

第三，检查每个实验版本是否使用相同的模型结构和相同的数据集划分，保证实验对比公平。

第四，检查模型是否能够输出 valid/test 的 AUC、PR-AUC、样本数、正样本数、正样本率和训练耗时。

第五，检查 Top5%、Top10%、Top20% 的真实购买率和召回率是否能够正常计算。

第六，检查实验汇总结果是否按照 test_pr_auc、test_auc、test_top10_precision 选择最优模型，并保存最优模型文件。

## 5. 测试环境

| 环境项 | 内容 |
|---|---|
| 开发语言 | Python |
| 主要依赖库 | pandas、numpy、scikit-learn、joblib |
| 模型类型 | SGD 逻辑回归概率模型 |
| 模型实现 | `SGDClassifier(loss="log_loss")` |
| 输入数据 | `ml_feature_wide_table_with_path.csv`、`feature_importance_with_path.csv` |
| 目标字段 | `label_buy_7d` |
| 测试方式 | 静态代码检查 + 流程测试设计 |

## 6. 配置文件测试

### 6.1 配置项检查

| 配置项             | 配置值                                                                       |
|:-------------------|:-----------------------------------------------------------------------------|
| 输入宽表路径       | ../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv |
| 特征重要性输入路径 | ../../../../form/deep_learning/with_path/feature_importance_with_path.csv    |
| 输出目录           | ../../../../form/deep_learning/top_20/feature_selection                      |
| 数据集字段         | dataset_type                                                                 |
| 训练/验证/测试标识 | train / valid / test                                                         |
| 目标标签           | label_buy_7d                                                                 |
| 不进入模型字段     | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d   |
| 特征筛选版本       | Top50、Top40、Top30、Top20                                                   |
| 模型参数           | random_state=42, max_iter=1000, tol=0.001, class_weight=balanced             |
| Top 评估比例       | 5%、10%、20%                                                                 |

### 6.2 配置测试结论

配置文件整体结构完整，已经将输入宽表路径、特征重要性文件路径、输出目录、数据集字段、目标字段、非建模字段、特征筛选版本、模型参数和 Top 比例集中管理。特征筛选版本设置为 Top50、Top40、Top30 和 Top20，能够满足多版本对比实验需要。Top 评估比例设置为 5%、10% 和 20%，适合用于推荐排序和营销触达场景下的高概率样本筛选。

## 7. 核心函数接口测试

| 函数名                           | 是否存在   | 测试说明                                                                 |
|:---------------------------------|:-----------|:-------------------------------------------------------------------------|
| resolve_path                     | 是         | 将相对路径转换为基于当前代码文件的绝对路径                               |
| build_model                      | 是         | 构建 imputer + scaler + SGDClassifier 的模型 Pipeline                    |
| make_xy                          | 是         | 从数据集中提取特征矩阵 X 和标签 y，并将特征转为 float32                  |
| evaluate_auc_pr                  | 是         | 计算 sample_count、positive_count、positive_rate、AUC、PR-AUC 和训练耗时 |
| evaluate_top_rates               | 是         | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率                          |
| run_feature_selection_experiment | 是         | 统一执行特征筛选实验、保存结果并返回最优实验                             |

核心代码的函数数量不多，但已经覆盖特征筛选实验的主要流程。`run_feature_selection_experiment(config)` 是统一入口，负责读取数据、构造特征集、训练多个模型、评估结果、汇总指标、选择最优模型并保存输出文件。

## 8. 实验流程测试

本模块完整实验流程如下：

```text
读取 68 字段特征宽表
→ 读取特征重要性文件
→ 转换目标标签 label_buy_7d
→ 自动选择数值型特征
→ 排除 dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d
→ 得到全部可建模特征 all_features
→ 根据特征重要性排序构造 Top50、Top40、Top30、Top20 特征集
→ 划分 train、valid、test
→ 对每个特征版本分别训练 SGD 逻辑回归模型
→ 预测 valid/test 购买概率
→ 计算 AUC、PR-AUC 和训练耗时
→ 计算 Top5%、Top10%、Top20% 命中效果
→ 保存每个实验版本的特征列表
→ 汇总各版本核心指标
→ 按 test_pr_auc、test_auc、test_top10_precision 选择最优实验
→ 保存最优模型
```

该流程能够保证各实验版本使用相同的数据集划分和相同模型结构，只有特征数量不同，因此实验对比具有公平性。

## 9. 静态检查结果

| 编号   | 检查项           | 检查方法                                     | 预期结果                                                                              | 实际结果                                                                                                                                                                                                   | 结论   |
|:-------|:-----------------|:---------------------------------------------|:--------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|
| SC001  | 配置字典解析     | 解析 FEATURE_SELECTION_CONFIG                | 配置字典能够正常解析                                                                  | 已成功解析配置字典                                                                                                                                                                                         | 通过   |
| SC002  | 输入文件路径配置 | 检查 data_path 和 feature_importance_path    | 同时配置特征宽表和特征重要性文件                                                      | data_path=../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv; feature_importance_path=../../../../form/deep_learning/with_path/feature_importance_with_path.csv                  | 通过   |
| SC003  | 特征筛选版本配置 | 检查 feature_set_sizes                       | 包含 Top50、Top40、Top30、Top20                                                       | [50, 40, 30, 20]                                                                                                                                                                                           | 通过   |
| SC004  | 非建模字段过滤   | 检查 drop_columns                            | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d 不进入模型 | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d                                                                                                                                 | 通过   |
| SC005  | 模型结构         | 检查 build_model                             | Pipeline 包含缺失值填充、标准化、SGD 逻辑回归                                         | 包含 SimpleImputer、StandardScaler、SGDClassifier(loss='log_loss')                                                                                                                                         | 通过   |
| SC006  | 类别不均衡处理   | 检查 class_weight                            | class_weight 使用 balanced 或从配置读取                                               | class_weight=balanced                                                                                                                                                                                      | 通过   |
| SC007  | 特征数值转换     | 检查 make_xy                                 | 特征列转为数值型并使用 float32                                                        | make_xy 中使用 pd.to_numeric(errors='coerce').astype('float32')                                                                                                                                            | 通过   |
| SC008  | TopK 评估优化    | 检查 evaluate_top_rates 是否使用 nlargest    | 使用 TopK 选择，不进行全量排序                                                        | 代码使用 prob.nlargest(top_n)                                                                                                                                                                              | 通过   |
| SC009  | 训练耗时记录     | 检查 time.perf_counter 和 train_time_seconds | 记录每个实验版本训练耗时                                                              | 代码使用 time.perf_counter，并在指标中输出 train_time_seconds                                                                                                                                              | 通过   |
| SC010  | 最优模型选择     | 检查 summary_df 排序逻辑                     | 根据 test_pr_auc、test_auc、test_top10_precision 选择最优版本                         | 代码按 test_pr_auc、test_auc、test_top10_precision 降序排序                                                                                                                                                | 通过   |
| SC011  | 输出文件设计     | 检查保存文件名                               | 输出 summary、metrics、top_rate、feature_list、best_model                             | 代码保存 feature_selection_summary_with_path.csv、feature_selection_metrics_with_path.csv、feature_selection_top_rate_metrics_with_path.csv、selected_feature_lists_with_path.csv 和 best_model_xxx.joblib | 通过   |
| SC012  | 运行入口         | 检查 run_feature_selection.py                | 调用统一接口并打印最优实验和输出路径                                                  | 运行入口调用 run_feature_selection_experiment(FEATURE_SELECTION_CONFIG)                                                                                                                                    | 通过   |

静态检查结果表明，当前特征筛选实验代码已经实现主要功能，包括多版本特征集构造、SGD 逻辑回归模型构建、AUC/PR-AUC 计算、Top 比例评估、训练耗时记录、最优模型选择和结果保存。需要注意的是，静态检查不能替代真实运行测试，后续仍需要使用真实宽表和特征重要性文件执行实验。

## 10. 测试用例与执行结果

| 用例编号   | 测试模块          | 测试内容                                                          | 测试输入                                                              | 预期结果                                                                                                            | 实际结果                                                   | 结论   |
|:-----------|:------------------|:------------------------------------------------------------------|:----------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------|:-----------------------------------------------------------|:-------|
| TC001      | 输入文件读取      | 读取新增行为路径特征宽表和特征重要性文件                          | ml_feature_wide_table_with_path.csv、feature_importance_with_path.csv | 两个输入文件均可正常读取                                                                                            | 需在本地真实路径下运行验证                                 | 待执行 |
| TC002      | 路径解析          | 将配置中的相对路径转换为绝对路径                                  | data_path、feature_importance_path、output_dir                        | 路径基于当前脚本位置正确解析                                                                                        | 代码已实现 resolve_path(base_file, relative_path)          | 通过   |
| TC003      | 标签转换          | 将 label_buy_7d 转为 int8                                         | 目标字段 label_buy_7d                                                 | 标签可用于模型训练和指标计算                                                                                        | 代码已实现 to_numeric、fillna(0)、astype('int8')           | 通过   |
| TC004      | 全部特征构建      | 自动选择全部数值型特征，并排除非建模字段                          | 特征宽表                                                              | 得到 all_features                                                                                                   | 代码已使用 select_dtypes 和 drop_columns 构造 all_features | 通过   |
| TC005      | 特征筛选版本构建  | 根据特征重要性排序构造 Top50、Top40、Top30、Top20 特征集          | feature_importance_with_path.csv                                      | 生成 all_features、top50_features、top40_features、top30_features、top20_features                                   | 代码已根据 ranked_features[:size] 构造多个特征集           | 通过   |
| TC006      | 数据集划分        | 按 dataset_type 划分 train、valid、test                           | dataset_type 字段                                                     | 得到 train_df、valid_df、test_df                                                                                    | 代码已按 train_value、valid_value、test_value 筛选数据     | 通过   |
| TC007      | 模型构建          | 构建 SGD 逻辑回归模型 Pipeline                                    | 模型配置参数                                                          | Pipeline 包含 imputer、scaler、clf                                                                                  | 代码使用 SimpleImputer + StandardScaler + SGDClassifier    | 通过   |
| TC008      | 多版本模型训练    | 依次训练 all、Top50、Top40、Top30、Top20 模型                     | feature_sets                                                          | 每个实验版本均完成训练并记录训练耗时                                                                                | 需在本地真实宽表和特征重要性文件下运行验证                 | 待执行 |
| TC009      | AUC / PR-AUC 评估 | 对 valid/test 计算 AUC 和 PR-AUC                                  | 真实标签和预测概率                                                    | 输出 experiment、feature_count、split、sample_count、positive_count、positive_rate、auc、pr_auc、train_time_seconds | 代码已实现 evaluate_auc_pr                                 | 通过   |
| TC010      | Top 比例评估      | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率                   | 真实标签、预测概率、top_rates                                         | 输出 top_rate、top_n、top_precision、top_recall                                                                     | 代码已实现 evaluate_top_rates，并使用 nlargest             | 通过   |
| TC011      | 特征列表输出      | 保存每个实验版本使用的特征列表                                    | feature_sets                                                          | 输出 selected_feature_lists_with_path.csv                                                                           | 代码已生成 feature_list_rows 并保存 CSV                    | 通过   |
| TC012      | 实验汇总          | 汇总每个实验版本 valid/test 指标和 test Top10% 指标               | metrics_df、top_df                                                    | 输出 feature_selection_summary_with_path.csv                                                                        | 代码已构造 summary_df                                      | 通过   |
| TC013      | 最优实验选择      | 根据 test_pr_auc、test_auc、test_top10_precision 排序选择最优版本 | summary_df                                                            | 返回 best_experiment 和 best_model_path                                                                             | 代码已实现排序并保存 best_model_xxx.joblib                 | 通过   |
| TC014      | 输出文件保存      | 保存 summary、metrics、top_rate、feature_list 和 best_model       | 实验结果 DataFrame 和最优模型                                         | 输出 4 个 CSV 文件和 1 个 joblib 模型文件                                                                           | 代码已实现 to_csv 和 joblib.dump                           | 通过   |
| TC015      | 运行入口          | 运行 python run_feature_selection.py                              | FEATURE_SELECTION_CONFIG                                              | 打印特征筛选实验完成、最优实验和输出文件路径                                                                        | 入口脚本已实现对应打印逻辑                                 | 通过   |

从测试用例看，当前大部分功能可以通过代码结构确认已经实现。需要依赖真实数据运行的部分主要是输入文件读取和多版本模型训练。正式提交前，应在本地运行 `python run_feature_selection.py`，确认程序能生成所有输出文件，并将 TC001 和 TC008 的结论补充为“通过”。

## 11. 输出文件测试

| 输出文件                                         | 说明                                                                        |
|:-------------------------------------------------|:----------------------------------------------------------------------------|
| feature_selection_summary_with_path.csv          | 汇总 all、Top50、Top40、Top30、Top20 各版本的核心指标，并按最优规则排序     |
| feature_selection_metrics_with_path.csv          | 保存每个实验版本在 valid/test 上的 AUC、PR-AUC、样本数、正样本率和训练耗时  |
| feature_selection_top_rate_metrics_with_path.csv | 保存每个实验版本在 valid/test 上 Top5%、Top10%、Top20% 的真实购买率和召回率 |
| selected_feature_lists_with_path.csv             | 保存每个实验版本使用的特征名称和排名                                        |
| best_model_xxx.joblib                            | 保存根据 test_pr_auc、test_auc、test_top10_precision 选择出的最优模型       |

输出文件设计完整，能够支持后续报告分析。其中，`feature_selection_summary_with_path.csv` 用于快速查看哪个特征版本最好；`feature_selection_metrics_with_path.csv` 用于详细查看 valid/test 的 AUC 和 PR-AUC；`feature_selection_top_rate_metrics_with_path.csv` 用于分析高概率样本命中效果；`selected_feature_lists_with_path.csv` 用于追踪每个实验版本具体使用了哪些特征；`best_model_xxx.joblib` 用于保存最优版本模型。

## 12. 最优实验选择逻辑测试

代码中最优实验不是随意指定，而是先汇总每个实验版本的 valid/test 指标和 test Top10% 指标，然后按照以下顺序排序：

```text
test_pr_auc
test_auc
test_top10_precision
```

排序方向均为降序。也就是说，模型优先选择 test PR-AUC 更高的版本；如果 PR-AUC 接近，再比较 test AUC；如果仍然接近，再比较 test Top10% 真实购买率。这个选择逻辑是合理的，因为购买预测任务中正样本相对更少，PR-AUC 更能反映模型对购买样本的识别能力，而 Top10% 真实购买率更贴近业务筛选高购买概率样本的使用场景。

## 13. 异常与风险测试

当前代码已经实现主要流程，但仍有一些需要注意的风险点：

第一，代码没有显式检查输入宽表是否缺少 `dataset_type`、`label_buy_7d` 或特征重要性文件中的 `feature` 字段。如果真实文件字段缺失，程序会在后续索引字段时自然报错。为了提高可读性，建议后续增加明确的字段检查提示。

第二，代码没有显式检查 train、valid、test 是否为空。如果某个数据集为空，模型训练或指标计算会报错。建议补充空集检查，提示用户检查 `dataset_type` 的取值。

第三，代码默认特征重要性文件中的特征名能够匹配宽表字段。如果匹配数量不足，Top50、Top40、Top30 或 Top20 实际可用特征数量可能小于预期。建议在构造特征集后检查每个版本的实际特征数量。

第四，`evaluate_auc_pr` 没有处理单一标签数据集。如果某个 valid/test 数据集中只有正样本或只有负样本，AUC 和 PR-AUC 会报错。建议参考主模型代码，增加单一标签时返回 NaN 的保护逻辑。

## 14. 时间复杂度与性能测试

| 步骤              | 时间复杂度       | 说明                                          |
|:------------------|:-----------------|:----------------------------------------------|
| 读取宽表          | O(n * d)         | 读取样本和全部字段                            |
| 读取特征重要性    | O(d)             | 读取特征排序结果                              |
| 标签转换          | O(n)             | 将 label_buy_7d 转为 int8                     |
| 全部特征筛选      | O(d)             | 选择数值型字段并排除非建模字段                |
| Top 特征集构建    | O(d)             | 根据重要性顺序截取 Top50、Top40、Top30、Top20 |
| 单个实验特征转换  | O(n * d_i)       | d_i 为当前实验版本特征数                      |
| 单个实验模型训练  | O(T * n * d_i)   | T 为迭代轮数，SGD 每轮线性扫描                |
| 单个实验预测      | O(m * d_i)       | m 为 valid/test 样本数                        |
| AUC / PR-AUC 计算 | O(m log m)       | 排序类指标需要按预测概率排序                  |
| Top 比例评估      | O(m log k)       | 使用 nlargest 取 TopK，避免完整排序           |
| 全部实验总成本    | Σ O(T * n * d_i) | 对 all、Top50、Top40、Top30、Top20 分别训练   |

设训练样本数为 `n`，验证集或测试集样本数为 `m`，当前实验版本的特征数量为 `d_i`，模型迭代轮数为 `T`，TopK 样本数量为 `k`。单个实验版本的训练复杂度为：

```text
O(T * n * d_i)
```

整个特征筛选实验需要训练多个版本，因此总体训练复杂度为：

```text
Σ O(T * n * d_i)
```

其中 `d_i` 分别对应全部特征、Top50、Top40、Top30 和 Top20。特征数量越少，训练和预测成本越低，因此特征筛选不仅可以提高模型解释性，也可能减少训练和预测时间。

Top 比例评估使用 `nlargest` 获取概率最高的 TopK 样本，而不是完整排序，因此复杂度为：

```text
O(m log k)
```

比完整排序的：

```text
O(m log m)
```

更适合只关注前 5%、10%、20% 高概率样本的业务场景。

## 15. 测试中发现的问题

第一，当前测试材料只有代码和说明文档，没有上传真实宽表、特征重要性输入文件和实验输出结果，因此无法直接验证实际 AUC、PR-AUC、Top10% 真实购买率、训练耗时和最优模型结果。

第二，当前代码没有对输入文件关键字段进行专门检查，例如宽表中的 `dataset_type`、`label_buy_7d`，以及特征重要性文件中的 `feature`。虽然字段缺失时程序会报错，但错误提示不够明确，建议补充更友好的检查逻辑。

第三，当前代码没有检查 train、valid、test 是否为空。为了避免模型训练或评估阶段报错，建议在数据集划分后增加空集检查。

第四，当前代码没有处理 valid/test 标签只有单一类别的情况。如果某个数据集标签只有一种取值，AUC 和 PR-AUC 无法正常计算，建议增加保护逻辑。

第五，特征筛选版本虽然配置为 Top50、Top40、Top30、Top20，但如果特征重要性文件和宽表字段匹配不足，实际特征数可能小于配置值。建议输出时检查每个版本实际特征数是否等于预期。

## 16. 改进建议

首先，建议在 `run_feature_selection_experiment` 中增加字段检查，明确检查宽表是否包含 `dataset_type` 和 `label_buy_7d`，并检查特征重要性文件是否包含 `feature` 字段。

其次，建议增加 train、valid、test 空集检查。如果某个数据集为空，应直接抛出清晰错误，提示用户检查 `dataset_type` 的取值。

再次，建议在构造 Top 特征集后打印或保存每个实验版本的实际特征数量。如果 Top50 实际只匹配到 45 个特征，需要提醒用户检查特征重要性文件是否与宽表字段一致。

最后，建议在实验完成后将 summary 表中的最优版本写入 README 或报告中，并保留训练耗时，这样可以同时说明模型效果和运行效率。

## 17. 本地运行验证步骤

在本地项目目录中准备好以下两个输入文件：

```text
ml_feature_wide_table_with_path.csv
feature_importance_with_path.csv
```

确认配置文件中的路径正确后，运行：

```bash
python run_feature_selection.py
```

运行成功后，应看到类似输出：

```text
特征筛选实验完成！
最优实验：top20_features

输出文件位置：
summary_path: ...
metrics_path: ...
top_path: ...
feature_list_path: ...
best_model_path: ...
```

随后检查输出目录中是否生成以下文件：

```text
feature_selection_summary_with_path.csv
feature_selection_metrics_with_path.csv
feature_selection_top_rate_metrics_with_path.csv
selected_feature_lists_with_path.csv
best_model_xxx.joblib
```

如果以上文件均正常生成，并且 summary 中能够选出最优实验，则说明特征筛选模块运行测试通过。

## 18. 测试结论

综合本次测试结果，特征筛选实验模块的代码结构基本完整，配置文件能够支持全部特征、Top50、Top40、Top30 和 Top20 多版本实验；核心代码能够完成特征集构造、模型训练、AUC/PR-AUC 评估、Top 比例评估、训练耗时记录、实验结果汇总、特征列表保存和最优模型保存；运行入口脚本也能够调用统一接口完成实验流程。

从静态检查角度看，本模块测试结论为：配置文件测试通过，核心函数封装测试通过，特征筛选版本构造测试通过，模型 Pipeline 测试通过，TopK 评估优化测试通过，输出文件设计测试通过。由于当前没有上传真实数据和实验输出结果，输入文件读取测试和多版本模型训练测试需要在本地运行后进一步确认。
