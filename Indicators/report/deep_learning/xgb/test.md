# XGBoost 购买概率模型测试文档

## 1. 文档说明

本文档用于测试“XGBoost 购买概率模型工程”。该工程基于新增行为路径特征后的 68 字段宽表，在前期特征筛选结果基础上训练 XGBoost 模型，并计划与 LR、LightGBM 模型进行对比。

本次上传的文件包括 XGBoost 配置文件、核心实验代码、README 说明和运行入口脚本。由于本次没有上传真实宽表、Top 特征列表文件和模型运行后的结果 CSV，因此本文档重点进行配置测试、代码流程测试、实验设计测试、输出文件测试和复杂度分析。实际 AUC、PR-AUC、Top10% 购买率、Brier Score、Log Loss 和最优实验结果需要本地运行后补充。

## 2. 测试对象

| 文件类型        | 文件名                       | 是否存在   | 文件大小     |
|:----------------|:-----------------------------|:-----------|:-------------|
| XGBoost配置文件 | config_xgb.py                | 是         | 1,469 bytes  |
| XGBoost说明文档 | README_XGBoost模型说明.md    | 是         | 894 bytes    |
| 运行入口脚本    | run_xgb_model.py             | 是         | 369 bytes    |
| XGBoost核心代码 | xgboost_purchase_pipeline.py | 是         | 11,912 bytes |

## 3. 模块背景

前一阶段已经完成 LR 购买概率模型、LightGBM 购买概率模型以及特征筛选实验。本阶段使用 XGBoost 进一步建模，目的是利用梯度提升树模型的非线性表达能力，观察它是否能够在新增行为路径特征的基础上取得更好的购买预测效果。

默认实验包括 4 个版本：

```text
xgb_top20_no_weight
xgb_top20_scale_pos_weight
xgb_all_features_no_weight
xgb_all_features_scale_pos_weight
```

其中，`top20` 表示使用特征筛选实验得到的 Top20 特征，`all_features` 表示使用全部可建模数值特征；`no_weight` 表示不额外设置类别权重，`scale_pos_weight` 表示根据训练集正负样本比例对正样本进行加权。

## 4. 测试目标

本次测试主要验证以下内容：

第一，检查 XGBoost 配置文件是否完整，包括输入路径、输出目录、字段配置、XGBoost 参数、实验特征集和样本权重选项。

第二，检查代码是否能够读取 68 字段宽表、Top20 特征列表，并构造 Top20 和全部特征两个特征版本。

第三，检查代码是否能够构造无权重和 `scale_pos_weight` 两种训练方式，形成 4 组对比实验。

第四，检查模型是否使用 XGBoost 二分类模型，并正确配置学习率、树数量、最大深度、最小子节点权重、采样比例和正则化参数。

第五，检查评估指标是否覆盖 AUC、PR-AUC、Brier Score、Log Loss、Top5%、Top10%、Top20% 真实购买率和召回率。

第六，检查是否能够输出实验汇总表、详细指标表、Top比例指标表、特征重要性表、最优模型预测结果、最优模型文件和最优特征列表。

第七，检查配置中的 LR/LGBM 对比文件路径是否被使用，并判断是否需要补充模型对比输出逻辑。

## 5. 测试环境

| 环境项 | 内容 |
|---|---|
| 开发语言 | Python |
| 主要依赖库 | pandas、numpy、scikit-learn、joblib、xgboost |
| 模型类型 | XGBoost 二分类模型 |
| 模型实现 | `XGBClassifier(objective="binary:logistic", eval_metric="aucpr")` |
| 输入数据 | `ml_feature_wide_table_with_path.csv`、`selected_feature_lists_with_path.csv` |
| 目标字段 | `label_buy_7d` |
| 输出概率字段 | `xgb_probability` |
| 测试方式 | 静态代码检查 + 流程测试设计 |

## 6. 配置文件测试

### 6.1 配置项检查

| 配置项              | 配置值                                                                                          |
|:--------------------|:------------------------------------------------------------------------------------------------|
| 输入宽表路径        | ../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv                    |
| Top特征列表路径     | ../../../../form/deep_learning/with_path/feature_selection/selected_feature_lists_with_path.csv |
| LR/LGBM对比文件路径 | ../../../../form/deep_learning/with_path/lgbm/model_comparison_lr_lgbm_with_path.csv            |
| 输出目录            | ../../../../form/deep_learning/with_path/xgboost                                                |
| 数据集字段          | dataset_type                                                                                    |
| 训练/验证/测试标识  | train / valid / test                                                                            |
| 目标标签            | label_buy_7d                                                                                    |
| 非建模字段          | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d                      |
| 预测结果保留字段    | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d                      |
| XGBoost核心参数     | n_estimators=120, learning_rate=0.08, max_depth=4, min_child_weight=5                           |
| 采样与正则参数      | subsample=0.85, colsample_bytree=0.85, reg_alpha=0.0, reg_lambda=1.0, max_bin=64                |
| 并行参数            | n_jobs=2                                                                                        |
| Top评估比例         | 5%、10%、20%                                                                                    |
| 实验特征集          | top20、all_features                                                                             |
| 权重实验选项        | no_weight、scale_pos_weight                                                                     |

### 6.2 配置测试结论

配置文件整体结构完整，已经设置了输入宽表路径、Top 特征列表路径、LR/LGBM 对比文件路径、输出目录、字段配置、XGBoost 模型参数、Top 评估比例、实验特征集和权重实验选项。默认会比较 Top20 特征和全部特征，并分别测试不加权和 `scale_pos_weight` 加权两种方式，因此可以同时观察“特征数量”和“样本不均衡处理”对模型效果的影响。

需要注意的是，配置文件中虽然写入了 `lr_lgbm_comparison_path`，但当前核心代码没有读取该路径，也没有生成 LR、LightGBM、XGBoost 三者的最终对比表。因此，如果最终报告需要完整对比三个模型，需要后续补充对比文件读取和合并输出逻辑。

## 7. 核心函数接口测试

| 函数名             | 是否存在   | 测试说明                                                          |
|:-------------------|:-----------|:------------------------------------------------------------------|
| resolve_path       | 是         | 将配置中的相对路径转换为基于当前文件的绝对路径                    |
| make_xy            | 是         | 从数据集中提取特征矩阵 X 和目标标签 y                             |
| prepare_data       | 是         | 对 train/valid/test 进行数值转换、缺失值中位数填充和 float32 转换 |
| build_model        | 是         | 根据配置构建 XGBoost 二分类模型                                   |
| evaluate_metrics   | 是         | 计算 AUC、PR-AUC、Brier Score、Log Loss 和训练耗时                |
| evaluate_top_rates | 是         | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率                   |
| run_xgb_experiment | 是         | 统一执行 XGBoost 多版本实验、保存结果并返回最优实验               |

核心代码已经覆盖 XGBoost 实验所需的主要流程。`run_xgb_experiment(config)` 是统一入口，负责读取数据、构造特征集、准备数据、训练多组 XGBoost 模型、评估指标、计算 Top 比例、输出特征重要性、保存最优预测结果和最优模型。

## 8. 实验流程测试

本模块完整实验流程如下：

```text
读取 68 字段特征宽表
→ 读取 selected_feature_lists_with_path.csv
→ 获取 Top20 特征列表
→ 自动选择全部数值型特征 all_features
→ 划分 train、valid、test
→ 根据训练集正负样本比例计算 scale_pos_weight
→ 构造 4 个实验版本
→ 对每个实验版本进行缺失值中位数填充
→ 训练 XGBoost 二分类模型
→ 输出 valid/test 购买概率
→ 计算 AUC、PR-AUC、Brier Score、Log Loss
→ 计算 Top5%、Top10%、Top20% 命中效果
→ 输出 gain 和 weight 两种特征重要性
→ 汇总各实验版本结果
→ 按 valid_pr_auc、valid_auc、test_pr_auc 选择最优实验
→ 保存最优模型、最优特征列表和最优预测结果
```

该流程可以比较 Top20 特征和全部特征两种特征输入，也可以比较是否使用 `scale_pos_weight` 处理样本不均衡，因此实验设计具有较好的对比意义。

## 9. 静态检查结果

| 编号   | 检查项                  | 检查方法                                                               | 预期结果                                                            | 实际结果                                                                                                                                                                                                                                                                                                                    | 结论   |
|:-------|:------------------------|:-----------------------------------------------------------------------|:--------------------------------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------|
| SC001  | 配置字典解析            | 解析 XGB_CONFIG                                                        | 配置字典能够正常解析                                                | 已成功解析配置字典                                                                                                                                                                                                                                                                                                          | 通过   |
| SC002  | 输入文件配置            | 检查 data_path、selected_feature_path、lr_lgbm_comparison_path         | 配置宽表、Top特征列表和LR/LGBM对比文件                              | data_path=../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv; selected_feature_path=../../../../form/deep_learning/with_path/feature_selection/selected_feature_lists_with_path.csv; lr_lgbm_comparison_path=../../../../form/deep_learning/with_path/lgbm/model_comparison_lr_lgbm_with_path.csv | 通过   |
| SC003  | 实验版本配置            | 检查 run_feature_sets 和 run_weight_options                            | 包含 top20、all_features，以及 no_weight、scale_pos_weight          | run_feature_sets=['top20', 'all_features']; run_weight_options=['no_weight', 'scale_pos_weight']                                                                                                                                                                                                                            | 通过   |
| SC004  | 非建模字段过滤          | 检查 drop_columns                                                      | ID、日期、标签字段不进入模型                                        | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d                                                                                                                                                                                                                                                  | 通过   |
| SC005  | XGBoost模型结构         | 检查 build_model                                                       | 使用 XGBClassifier，objective='binary:logistic'，tree_method='hist' | 代码使用 XGBClassifier，并配置 binary:logistic、aucpr、hist                                                                                                                                                                                                                                                                 | 通过   |
| SC006  | 类别不均衡实验          | 检查 scale_pos_weight 计算与传入                                       | 支持无权重和 scale_pos_weight 两种实验                              | 代码根据 train_neg / train_pos 计算 scale_pos_weight，并构造 no_weight 与 scale_pos_weight 实验                                                                                                                                                                                                                             | 通过   |
| SC007  | Top20特征读取           | 检查 selected_feature_lists_with_path.csv 中 top20_features 的读取逻辑 | 能够从特征筛选结果中读取 top20_features                             | 代码按 experiment == 'top20_features' 读取并按 feature_rank 排序                                                                                                                                                                                                                                                            | 通过   |
| SC008  | 缺失值处理              | 检查 prepare_data                                                      | 使用 SimpleImputer(strategy='median') 对特征缺失值填充              | 代码使用 SimpleImputer(strategy='median')                                                                                                                                                                                                                                                                                   | 通过   |
| SC009  | 指标计算完整性          | 检查 evaluate_metrics                                                  | 输出 AUC、PR-AUC、Brier Score、Log Loss 和 train_time_seconds       | 代码包含 roc_auc_score、average_precision_score、brier_score_loss、log_loss、train_time_seconds                                                                                                                                                                                                                             | 通过   |
| SC010  | TopK评估优化            | 检查 evaluate_top_rates 是否使用 nlargest                              | 使用 TopK 选择而不是完整排序                                        | 代码使用 prob.nlargest(top_n)                                                                                                                                                                                                                                                                                               | 通过   |
| SC011  | 特征重要性输出          | 检查 get_booster().get_score                                           | 输出 importance_gain 和 importance_weight                           | 代码使用 importance_type='gain' 和 importance_type='weight'                                                                                                                                                                                                                                                                 | 通过   |
| SC012  | 最优实验选择            | 检查 summary_df 排序逻辑                                               | 按 valid_pr_auc、valid_auc、test_pr_auc 选择最优实验                | 代码按 valid_pr_auc、valid_auc、test_pr_auc 降序选择 best_exp                                                                                                                                                                                                                                                               | 通过   |
| SC013  | 输出文件保存            | 检查输出文件名和 joblib.dump                                           | 保存 summary、metrics、top、importance、prediction、model、features | 代码保存 5 个 CSV、最优模型 joblib 和最优特征 csv                                                                                                                                                                                                                                                                           | 通过   |
| SC014  | LR/LGBM对比文件使用情况 | 检查核心代码是否读取 lr_lgbm_comparison_path                           | 如果配置了对比文件，代码应读取并用于后续对比                        | 配置中存在 lr_lgbm_comparison_path，但核心代码未读取该字段                                                                                                                                                                                                                                                                  | 需改进 |
| SC015  | 运行入口                | 检查 run_xgb_model.py                                                  | 调用 run_xgb_experiment(XGB_CONFIG)                                 | 入口脚本调用统一接口，并打印最优实验和输出路径                                                                                                                                                                                                                                                                              | 通过   |

静态检查结果表明，当前 XGBoost 工程已经实现主要功能，包括实验版本构造、类别不均衡处理、缺失值填充、XGBoost 模型训练、指标计算、TopK 评估、特征重要性输出、最优实验选择和结果保存。需要注意的是，`lr_lgbm_comparison_path` 虽然在配置文件中存在，但当前核心代码未使用它，因此三模型对比功能仍需补充。

## 10. 测试用例与执行结果

| 用例编号   | 测试模块       | 测试内容                                                            | 测试输入                                                                                                          | 预期结果                                                                                                                      | 实际结果                                                        | 结论   |
|:-----------|:---------------|:--------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------|:----------------------------------------------------------------|:-------|
| TC001      | 输入文件读取   | 读取 68 字段特征宽表、Top特征列表和LR/LGBM对比文件                  | ml_feature_wide_table_with_path.csv、selected_feature_lists_with_path.csv、model_comparison_lr_lgbm_with_path.csv | 输入文件均可正常读取                                                                                                          | 需在本地真实路径下运行验证；当前代码实际只读取宽表和Top特征列表 | 待执行 |
| TC002      | Top20特征构建  | 从 selected_feature_lists_with_path.csv 中读取 top20_features       | selected_feature_lists_with_path.csv                                                                              | 按 feature_rank 得到 Top20 特征列表                                                                                           | 代码已实现 experiment == 'top20_features' 的筛选和排序          | 通过   |
| TC003      | 全部特征构建   | 自动选择全部数值型特征，并排除非建模字段                            | 68 字段特征宽表                                                                                                   | 得到 all_features，且不包含 ID、日期、标签字段                                                                                | 代码已实现 select_dtypes + drop_columns 过滤                    | 通过   |
| TC004      | 实验组合构建   | 组合 top20/all_features 和 no_weight/scale_pos_weight               | run_feature_sets、run_weight_options                                                                              | 生成 4 个实验：xgb_top20_no_weight、xgb_top20_scale_pos_weight、xgb_all_features_no_weight、xgb_all_features_scale_pos_weight | 代码已根据配置动态构造实验列表                                  | 通过   |
| TC005      | 缺失值处理     | 对 train/valid/test 特征进行中位数填充                              | X_train_raw、X_valid_raw、X_test_raw                                                                              | 训练集 fit imputer，验证集和测试集 transform                                                                                  | 代码已实现 SimpleImputer(strategy='median')                     | 通过   |
| TC006      | 模型构建       | 构建 XGBoost 二分类模型                                             | XGB_CONFIG                                                                                                        | XGBClassifier 参数正确，objective=binary:logistic，eval_metric=aucpr，tree_method=hist                                        | 代码已实现 build_model(config, scale_pos_weight)                | 通过   |
| TC007      | 样本不均衡处理 | 计算 scale_pos_weight 并用于加权实验                                | 训练集正负样本数量                                                                                                | scale_pos_weight = train_neg / train_pos                                                                                      | 代码已实现该计算逻辑                                            | 通过   |
| TC008      | 模型训练       | 训练 4 个 XGBoost 实验版本                                          | train_df、valid_df、test_df                                                                                       | 4 个实验均训练完成，并记录 train_time_seconds                                                                                 | 需在本地真实数据路径下运行验证                                  | 待执行 |
| TC009      | 整体指标评估   | 对 valid/test 计算 AUC、PR-AUC、Brier Score、Log Loss               | 真实标签 y_true 和预测概率 prob                                                                                   | 输出 sample_count、positive_count、positive_rate、auc、pr_auc、brier_score、log_loss、train_time_seconds                      | 代码已实现 evaluate_metrics                                     | 通过   |
| TC010      | Top比例评估    | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率                     | 真实标签、预测概率、top_rates                                                                                     | 输出 top_rate、top_n、top_precision、top_recall                                                                               | 代码已使用 nlargest 实现 TopK 评估                              | 通过   |
| TC011      | 特征重要性     | 输出 XGBoost gain 和 weight 两类重要性                              | 训练后的 booster 和特征列表                                                                                       | 输出 experiment、feature、importance_gain、importance_weight、rank_gain                                                       | 代码已实现 booster.get_score                                    | 通过   |
| TC012      | 最优实验选择   | 根据 valid_pr_auc、valid_auc、test_pr_auc 选择最优实验              | summary_df                                                                                                        | 返回 best_experiment，并保存对应模型、imputer 和特征列表                                                                      | 代码已实现 best_exp 选择和 joblib.dump                          | 通过   |
| TC013      | 预测结果保存   | 保存最优实验的 valid/test 预测概率                                  | best_exp 对应 valid_prob、test_prob                                                                               | 生成 xgb_predictions_best_with_path.csv，包含 id_columns 和 xgb_probability                                                   | 代码已实现 prediction_result 保存                               | 通过   |
| TC014      | 输出文件保存   | 保存 summary、metrics、top、importance、prediction、model、features | 各类实验结果                                                                                                      | 输出 5 个 CSV、1 个 joblib 模型包、1 个最优特征 CSV                                                                           | 代码已实现全部输出保存                                          | 通过   |
| TC015      | 运行入口       | 运行 python run_xgb_model.py                                        | XGB_CONFIG                                                                                                        | 打印实验完成、最优实验和输出文件路径                                                                                          | 入口脚本已实现对应逻辑                                          | 通过   |

从测试用例看，当前大部分功能都可以通过代码结构确认已经实现。需要依赖真实数据运行的测试主要是输入文件读取和模型训练。正式提交前，应在本地运行 `python run_xgb_model.py`，确认 4 个实验版本均能训练完成，并生成所有输出文件。

## 11. 输出文件测试

| 输出文件                             | 说明                                                                             |
|:-------------------------------------|:---------------------------------------------------------------------------------|
| xgb_experiment_summary_with_path.csv | 汇总各 XGBoost 实验版本的 valid/test 指标、Top10效果和训练耗时                   |
| xgb_model_metrics_with_path.csv      | 保存每个实验版本在 valid/test 上的 AUC、PR-AUC、Brier Score、Log Loss 和训练耗时 |
| xgb_top_rate_metrics_with_path.csv   | 保存每个实验版本在 valid/test 上 Top5%、Top10%、Top20% 的真实购买率和召回率      |
| xgb_feature_importance_with_path.csv | 保存 XGBoost 的 gain 和 weight 两类特征重要性                                    |
| xgb_predictions_best_with_path.csv   | 保存最优实验在 valid/test 上的预测概率 xgb_probability                           |
| best_xgb_model_xxx.joblib            | 保存最优 XGBoost 模型、缺失值填充器、特征列表、实验名称和字段配置                |
| best_xgb_features_xxx.csv            | 保存最优实验使用的特征列表                                                       |

输出文件设计较完整，包含实验汇总和详细指标，也包含 Top 比例业务指标、XGBoost 特征重要性、最优模型预测结果、最优模型包和最优特征列表。尤其是 `best_xgb_model_xxx.joblib` 中保存了模型、缺失值填充器、特征列表、实验名称、目标字段和 ID 字段配置，便于后续复用模型进行预测。

## 12. 指标测试设计

XGBoost 模型输出的是购买概率，因此评价指标不能只看准确率。本模块使用以下指标：

| 指标 | 作用 |
|---|---|
| AUC | 衡量模型区分正负样本的整体排序能力 |
| PR-AUC | 更关注正样本识别，适合正负样本不均衡场景 |
| Brier Score | 衡量概率预测误差，越小越好 |
| Log Loss | 衡量概率预测损失，越小越好 |
| Top Precision | 预测概率最高的一部分样本中的真实购买率 |
| Top Recall | 预测概率最高的一部分样本覆盖了多少真实购买样本 |
| Train Time | 衡量不同实验版本的训练成本 |

其中，PR-AUC 和 Top 比例指标对本项目最重要。因为购买样本通常少于未购买样本，PR-AUC 比普通准确率更能反映模型对购买样本的识别能力；而 Top5%、Top10%、Top20% 真实购买率更贴近推荐排序和营销触达场景。

## 13. 最优实验选择逻辑测试

代码中最优实验选择顺序为：

```text
valid_pr_auc
valid_auc
test_pr_auc
```

排序方向均为降序。也就是说，模型优先选择验证集 PR-AUC 更高的实验版本；如果验证集 PR-AUC 接近，再比较验证集 AUC；如果仍然接近，再比较测试集 PR-AUC。这个逻辑相对稳妥，因为验证集用于模型选择，测试集更多用于最终验证，避免直接完全按照测试集结果选择模型造成结果偏乐观。

## 14. 与 LR 和 LightGBM 版本的关系

XGBoost 工程不是孤立的模型实验，而是在 LR 和 LightGBM 之后进行的进一步对比实验。它需要使用前一阶段输出的 `selected_feature_lists_with_path.csv` 读取 Top20 特征，并与全部特征版本进行对比。相比 SGD 逻辑回归，XGBoost 可以学习非线性关系和特征交互；相比 LightGBM，XGBoost 的训练机制和树生长方式不同，因此可以作为另一个强基线模型进行比较。

当前配置文件中已经预留了 `lr_lgbm_comparison_path`，说明设计上希望把 XGBoost 与 LR、LightGBM 进行汇总对比。但当前核心代码没有读取该文件，因此模型对比还没有真正落地。后续可以在实验完成后将 XGBoost summary 与 LR/LGBM comparison 表合并，形成最终模型对比表。

## 15. 异常与风险测试

当前代码已经实现主要流程，但仍有以下风险需要注意：

第一，代码没有显式检查输入文件是否存在。如果 `ml_feature_wide_table_with_path.csv` 或 `selected_feature_lists_with_path.csv` 路径错误，程序会在读取 CSV 时直接报错。建议后续增加文件存在性检查，并输出更友好的提示。

第二，代码没有显式检查字段完整性，例如宽表中的 `dataset_type`、`label_buy_7d`，以及特征列表文件中的 `experiment`、`feature_rank`、`feature`。如果字段缺失，后续筛选时会报错。建议增加专门的字段检查函数。

第三，代码计算 `scale_pos_weight = train_neg / train_pos`，如果训练集正样本数量为 0，会发生除零错误。虽然正常购买预测数据中应当存在正样本，但为了增强稳定性，建议增加保护逻辑。

第四，代码没有检查 Top20 特征实际匹配数量。如果特征列表中的字段名与宽表字段不一致，`top20_features` 可能不足 20 个。建议训练前打印并检查实际特征数量。

第五，当前配置中存在 LR/LGBM 对比文件路径，但核心代码没有使用该路径，导致最终输出中缺少 LR、LightGBM、XGBoost 三模型合并对比结果。

第六，当前代码没有设置 early stopping。虽然配置了 `eval_metric="aucpr"`，但模型训练时没有传入验证集用于早停，因此可能存在训练轮数不够或训练过度的问题。后续可以考虑加入 early stopping，以提高模型稳定性。

## 16. 时间复杂度与性能测试

| 步骤                  | 时间复杂度                | 说明                                                          |
|:----------------------|:--------------------------|:--------------------------------------------------------------|
| 读取宽表              | O(n * d)                  | 读取 68 字段特征宽表                                          |
| 读取 Top 特征列表     | O(d)                      | 读取 selected_feature_lists_with_path.csv                     |
| 构造 all_features     | O(d)                      | 选择数值型字段并排除非建模字段                                |
| 构造 top20_features   | O(d)                      | 按 feature_rank 筛选并匹配宽表字段                            |
| 缺失值填充            | O(n * d_i)                | 对当前实验特征集使用中位数填充                                |
| 单个 XGBoost 模型训练 | 约 O(T * n * d_i * log n) | T 为树数量，d_i 为当前实验特征数，hist 方法会减少分裂搜索成本 |
| 预测概率              | O(m * T * depth)          | m 为 valid/test 样本数，depth 为树深度                        |
| AUC / PR-AUC          | O(m log m)                | 排序类指标需要按预测概率排序                                  |
| Top 比例评估          | O(m log k)                | 使用 nlargest 取 TopK                                         |
| 特征重要性输出        | O(d_i)                    | 读取 booster 的 gain 和 weight 重要性                         |
| 全部实验总成本        | Σ 单实验成本              | 默认训练 4 个实验版本                                         |

设样本数为 `n`，当前实验使用的特征数量为 `d_i`，树数量为 `T`，验证集或测试集样本数为 `m`，树最大深度为 `depth`，TopK 样本数量为 `k`。单个 XGBoost 实验的训练复杂度可以近似理解为：

```text
O(T * n * d_i * log n)
```

实际复杂度会受到 `max_depth`、`max_bin`、`subsample`、`colsample_bytree` 和 `tree_method="hist"` 的影响。预测复杂度近似为：

```text
O(m * T * depth)
```

由于默认会训练 4 个实验版本，因此总体训练成本是多个实验版本训练成本的总和。Top 比例评估使用 `nlargest`，复杂度为：

```text
O(m log k)
```

比完整排序的 `O(m log m)` 更适合只关注高概率候选样本的场景。

## 17. 本地运行验证步骤

在本地项目目录中准备以下输入文件：

```text
ml_feature_wide_table_with_path.csv
selected_feature_lists_with_path.csv
```

如果后续要做 LR、LightGBM、XGBoost 三模型对比，还需要准备：

```text
model_comparison_lr_lgbm_with_path.csv
```

确认已经安装 XGBoost：

```bash
python -m pip install xgboost
```

然后运行：

```bash
python run_xgb_model.py
```

运行成功后，应看到类似输出：

```text
XGBoost 购买概率模型实验完成！
最优实验：xgb_top20_scale_pos_weight

输出文件位置：
summary_path: ...
metrics_path: ...
top_path: ...
importance_path: ...
prediction_path: ...
model_path: ...
features_path: ...
```

随后检查输出目录中是否生成所有 XGBoost 结果文件，并重点查看 `xgb_experiment_summary_with_path.csv` 中哪个实验版本最优。

## 18. 改进建议

首先，建议增加输入文件和字段检查函数，明确检查宽表、Top 特征列表和 LR/LGBM 对比文件是否存在，以及关键字段是否完整。

其次，建议在构造 Top20 特征后检查实际特征数量。如果不足 20 个，应输出警告，提示特征列表和宽表字段可能不一致。

再次，建议增加 `scale_pos_weight` 除零保护。如果训练集中正样本数为 0，应停止训练并给出明确提示。

第四，建议补充 early stopping。可以使用验证集作为 eval_set，并设置 early_stopping_rounds，避免固定树数量导致过拟合或欠拟合。

最后，建议真正使用配置中的 `lr_lgbm_comparison_path`，将 XGBoost 最优结果与 LR、LightGBM 对比结果合并，输出最终的三模型对比表。

## 19. 测试结论

综合本次测试结果，XGBoost 购买概率模型工程的代码结构基本完整。配置文件能够支持 Top20 和全部特征两种特征集，也能够支持无权重和 `scale_pos_weight` 两种样本不均衡处理方式。核心代码已经实现数据读取、特征构造、缺失值填充、XGBoost 模型训练、概率预测、指标评估、Top 比例评估、特征重要性输出、最优实验选择和结果保存。运行入口脚本也能够调用统一接口完成完整流程。

从静态检查角度看，本模块测试结论为：配置文件测试通过，核心函数封装测试通过，XGBoost 模型结构测试通过，样本不均衡处理测试通过，TopK 评估测试通过，输出文件设计测试通过。需要改进的是，配置中的 `lr_lgbm_comparison_path` 当前未被核心代码使用，三模型对比功能还需要补充。由于当前没有上传真实数据和实验输出结果，输入文件读取测试和 4 个 XGBoost 实验训练测试需要在本地运行后进一步确认。
