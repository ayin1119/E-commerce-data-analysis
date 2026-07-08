# 新增行为路径特征版本购买概率模型测试文档

## 1. 文档说明

本文档用于测试“新增行为路径特征版本”的购买概率模型代码。该版本基于新版 68 字段特征宽表，相比旧版 65 字段模型，新增了 3 个行为路径特征，并在配置文件和核心代码中加入了必需字段检查逻辑，避免误用旧版宽表。

本测试文档根据当前上传的配置文件、核心封装代码、运行入口脚本和 README 说明编写。由于本次没有上传真实 68 字段宽表和模型运行后的结果文件，因此本文档重点验证代码封装、配置项、路径特征检查、输出文件设计、异常处理和运行流程。AUC、PR-AUC、Top10% 购买率等实际指标需要在本地运行模型后补充。

## 2. 测试对象

| 文件类型         | 文件名                              | 是否存在   | 文件大小     |
|:-----------------|:------------------------------------|:-----------|:-------------|
| 配置文件         | config(4).py                        | 是         | 2,317 bytes  |
| 核心封装代码     | purchase_probability_pipeline(3).py | 是         | 12,997 bytes |
| 新增行为路径说明 | README_新增行为路径特征说明.md      | 是         | 1,637 bytes  |
| 运行入口脚本     | run_purchase_model(3).py            | 是         | 561 bytes    |

## 3. 版本背景

本版本的核心变化是将原来的 65 字段购买概率模型升级为新增行为路径特征的 68 字段版本。新增字段包括：

```text
pre_buy_behavior_count
purchase_count
pre_buy_behavior_per_purchase
```

这三个字段用于描述用户购买前的行为路径信息，例如购买前发生过多少浏览、收藏、加购等行为，以及购买前行为与购买次数之间的关系。相比只使用普通行为统计特征，路径特征能够补充“购买前行为过程”的信息，有助于模型更好地理解用户从浏览到购买的转化过程。

## 4. 测试目标

本次测试主要验证以下内容：

第一，检查配置文件是否正确指向新增行为路径特征后的 68 字段宽表。

第二，检查配置文件中是否声明了 3 个新增行为路径特征，并将它们作为必须存在字段进行校验。

第三，检查核心代码是否能够在读取数据后检查新增路径特征，如果字段缺失能够及时报错，防止旧版 65 字段宽表被误用。

第四，检查新增行为路径特征是否能够自动进入模型特征列，而不需要手动写入固定特征列表。

第五，检查模型训练、概率预测、AUC/PR-AUC 评估、Top 比例评估、特征重要性输出和结果保存流程是否完整。

第六，检查输出文件是否带有 `with_path` 标识，避免覆盖旧版模型结果。

## 5. 测试环境

| 环境项 | 内容 |
|---|---|
| 开发语言 | Python |
| 主要依赖库 | pandas、numpy、scikit-learn、joblib |
| 模型类型 | SGD 逻辑回归概率模型 |
| 模型实现 | `SGDClassifier(loss="log_loss")` |
| 输入数据 | 新版 68 字段特征宽表 `ml_feature_wide_table_with_path.csv` |
| 目标字段 | `label_buy_7d` |
| 输出字段 | `buy_probability` |
| 测试方式 | 静态代码检查 + 流程测试设计 |

## 6. 配置文件测试

### 6.1 配置项检查

| 配置项               | 配置值                                                                       |
|:---------------------|:-----------------------------------------------------------------------------|
| 输入宽表路径         | ../../../../form/deep_learning/with_path/ml_feature_wide_table_with_path.csv |
| 输出目录             | ../../../../form/deep_learning/with_path                                     |
| 数据集字段           | dataset_type                                                                 |
| 训练/验证/测试标识   | train / valid / test                                                         |
| 目标标签             | label_buy_7d                                                                 |
| 不进入模型字段       | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d   |
| 预测结果保留字段     | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d   |
| 新增行为路径必需字段 | pre_buy_behavior_count、purchase_count、pre_buy_behavior_per_purchase        |
| 模型参数             | random_state=42, max_iter=1000, tol=0.001, class_weight=balanced             |
| 是否转 float32       | True                                                                         |
| Top 评估比例         | 5%、10%、20%                                                                 |
| 特征重要性 TopN      | 50                                                                           |
| 模型文件名           | purchase_probability_model_with_path.joblib                                  |
| 模型指标文件名       | model_metrics_with_path.csv                                                  |
| Top 指标文件名       | top_rate_metrics_with_path.csv                                               |
| 特征重要性文件名     | feature_importance_with_path.csv                                             |
| 预测结果文件名       | purchase_probability_predictions_with_path.csv                               |

### 6.2 配置测试结论

配置文件整体结构完整，已经将输入路径、输出目录、目标字段、非建模字段、新增行为路径字段、模型参数、Top 评估比例和输出文件名统一管理。其中，`required_feature_columns` 明确列出了 3 个新增行为路径特征，说明该版本不再只是普通 65 字段模型，而是针对 68 字段宽表进行建模。

输出文件名均带有 `with_path`，例如 `purchase_probability_model_with_path.joblib`、`model_metrics_with_path.csv` 和 `purchase_probability_predictions_with_path.csv`，这样可以避免覆盖旧版模型结果，便于后续做新旧模型对比。

## 7. 核心函数接口测试

| 函数名                         | 是否存在   | 测试说明                                                             |
|:-------------------------------|:-----------|:---------------------------------------------------------------------|
| load_data                      | 是         | 根据配置路径读取新增行为路径特征宽表                                 |
| check_required_columns         | 是         | 检查数据集字段、目标字段和 3 个新增行为路径字段是否存在              |
| get_feature_columns            | 是         | 自动选择数值型特征并排除非建模字段，同时打印新增路径特征是否进入模型 |
| optimize_memory                | 是         | 将特征转为数值型和 float32，标签转为 int8                            |
| split_dataset                  | 是         | 按 dataset_type 划分 train、valid、test，并检查空集                  |
| make_xy                        | 是         | 拆分模型输入 X 和目标标签 y                                          |
| build_model                    | 是         | 构建 SimpleImputer + StandardScaler + SGDClassifier Pipeline         |
| train_model                    | 是         | 训练购买概率模型                                                     |
| predict_probability            | 是         | 输出未来 7 天购买概率                                                |
| evaluate_auc_metrics           | 是         | 计算样本数、正样本数、正样本率、AUC、PR-AUC                          |
| evaluate_top_rates             | 是         | 计算 Top5%、Top10%、Top20% 真实购买率和召回率                        |
| build_prediction_result        | 是         | 保存 ID 字段、真实标签和预测概率                                     |
| get_feature_importance         | 是         | 提取逻辑回归系数，输出 TopN 重要特征                                 |
| save_outputs                   | 是         | 保存模型、指标、Top 指标、特征重要性和预测结果                       |
| run_purchase_probability_model | 是         | 统一接口，完成读取、训练、预测、评估、保存全流程                     |

核心代码已经封装了完整流程，从读取数据、字段检查、特征选择、内存优化、数据集划分，到模型训练、概率预测、指标评估、Top 比例评估、预测结果输出、特征重要性输出和文件保存，最后由统一接口 `run_purchase_probability_model(config)` 串联执行。

## 8. 新增行为路径特征检查测试

本版本最重要的测试点是确认新增行为路径特征是否真实进入新版宽表和模型训练过程。代码中通过两层逻辑进行保证。

第一层是在 `check_required_columns` 中检查必要字段。除了检查 `dataset_type` 和 `label_buy_7d`，代码还会读取配置中的 `required_feature_columns`，把 3 个新增行为路径特征加入必要字段列表。如果新版宽表中缺少其中任何一个字段，程序会直接抛出 `ValueError`，提示缺少必要字段。

第二层是在 `get_feature_columns` 中自动选择数值型特征，并排除 ID、日期、标签等非建模字段。由于新增行为路径特征是数值型字段，并且没有出现在 `drop_columns` 中，因此它们会自动进入模型。代码还会打印“新增行为路径特征进入模型”，用于确认这三个字段是否被实际选入特征列表。

因此，该版本能够有效防止两个问题：一是误用旧版 65 字段宽表；二是虽然宽表中存在新增字段，但没有进入模型训练。

## 9. 静态检查结果

| 编号   | 检查项                   | 检查方法                                                         | 预期结果                                                                   | 实际结果                                                                                                 | 结论   |
|:-------|:-------------------------|:-----------------------------------------------------------------|:---------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------|:-------|
| SC001  | 配置字典可解析           | 读取 config(4).py 并解析 PURCHASE_MODEL_CONFIG                   | 配置字典能够正常解析                                                       | 已成功解析配置字典                                                                                       | 通过   |
| SC002  | 新增行为路径字段配置     | 检查 required_feature_columns                                    | 包含 pre_buy_behavior_count、purchase_count、pre_buy_behavior_per_purchase | pre_buy_behavior_count、purchase_count、pre_buy_behavior_per_purchase                                    | 通过   |
| SC003  | 旧版结果防覆盖           | 检查输出文件名是否带 with_path                                   | 输出文件名与旧版 65 字段模型区分                                           | 模型、指标、Top指标、特征重要性、预测结果文件名均带 with_path                                            | 通过   |
| SC004  | 非建模字段过滤           | 检查 drop_columns                                                | ID、日期、标签字段不进入模型                                               | drop_columns 包含 dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d             | 通过   |
| SC005  | 必要字段检查逻辑         | 检查 check_required_columns 是否 extend required_feature_columns | 除了 dataset_col 和 target_col，也检查新增行为路径字段                     | 代码中已将 config.get('required_feature_columns', []) 加入必要字段检查                                   | 通过   |
| SC006  | 新增路径特征进入模型提示 | 检查 get_feature_columns 是否打印 used_required_features         | 能显示新增行为路径特征是否进入模型                                         | 代码中会打印“新增行为路径特征进入模型”                                                                   | 通过   |
| SC007  | 模型 Pipeline 结构       | 检查 build_model                                                 | 包含缺失值填充、标准化、SGD 逻辑回归                                       | 包含 SimpleImputer、StandardScaler、SGDClassifier(loss='log_loss')                                       | 通过   |
| SC008  | 样本不均衡处理           | 检查 class_weight                                                | 使用 balanced 或从配置读取                                                 | SGDClassifier 中 class_weight 从配置读取，默认 balanced                                                  | 通过   |
| SC009  | TopK 评估优化            | 检查 evaluate_top_rates 是否使用 nlargest                        | 使用 TopK，不进行完整排序                                                  | 代码使用 prob.nlargest(top_n)                                                                            | 通过   |
| SC010  | 运行入口                 | 检查 run_purchase_model(3).py                                    | 调用统一接口并打印输出                                                     | 入口脚本调用 run_purchase_probability_model(PURCHASE_MODEL_CONFIG)，并打印特征数量、数据集形状和输出路径 | 通过   |

静态检查结果表明，当前版本已经完成新增行为路径特征相关的配置和代码修改。配置文件声明了 3 个新增字段，核心代码会检查这些字段是否存在，并在自动特征选择阶段提示新增特征是否进入模型。模型 Pipeline、TopK 评估、特征重要性输出和运行入口也都保持完整。

## 10. 测试用例与执行结果

| 用例编号   | 测试模块       | 测试内容                                                 | 测试输入                                                              | 预期结果                                                            | 实际结果                                                            | 结论   |
|:-----------|:---------------|:---------------------------------------------------------|:----------------------------------------------------------------------|:--------------------------------------------------------------------|:--------------------------------------------------------------------|:-------|
| TC001      | 输入文件读取   | 读取 68 字段新版宽表 ml_feature_wide_table_with_path.csv | 配置中的 data_path                                                    | 能够正常读取 DataFrame                                              | 需在本地真实宽表路径下运行验证                                      | 待执行 |
| TC002      | 新增字段校验   | 检查 3 个行为路径字段是否存在                            | pre_buy_behavior_count、purchase_count、pre_buy_behavior_per_purchase | 字段存在时通过；字段缺失时抛出 ValueError                           | 代码已实现 required_feature_columns 检查逻辑                        | 通过   |
| TC003      | 旧版宽表防误用 | 使用缺少新增路径字段的 65 字段旧宽表运行                 | 旧版 65 字段宽表                                                      | 程序报错并提示缺少必要字段                                          | 代码中已设计字段缺失时报错逻辑                                      | 通过   |
| TC004      | 特征选择       | 自动选择数值型特征并排除非建模字段                       | 新版 68 字段宽表                                                      | 新增行为路径特征进入 feature_columns，ID/日期/标签不进入模型        | 代码已实现 select_dtypes + drop_columns，并打印新增特征进入模型情况 | 通过   |
| TC005      | 内存优化       | 将特征列转为 float32，标签转为 int8                      | feature_columns 和 label_buy_7d                                       | 降低内存占用，标签格式正确                                          | 代码已实现 to_numeric、float32、int8 转换                           | 通过   |
| TC006      | 数据集划分     | 按 dataset_type 划分 train、valid、test                  | 包含 train、valid、test 的宽表                                        | 三个数据集均非空                                                    | 代码已实现空集检查，空集时抛出 ValueError                           | 通过   |
| TC007      | 模型构建       | 构建购买概率模型 Pipeline                                | PURCHASE_MODEL_CONFIG                                                 | Pipeline 包含 imputer、scaler、clf                                  | 代码使用 SimpleImputer + StandardScaler + SGDClassifier             | 通过   |
| TC008      | 模型训练       | 使用训练集训练新增路径特征版本模型                       | X_train、y_train                                                      | 模型训练完成，可调用 predict_proba                                  | 需在本地真实宽表路径下运行验证                                      | 待执行 |
| TC009      | 概率预测       | 对 valid/test 输出 buy_probability                       | X_valid、X_test                                                       | 输出 0 到 1 之间的购买概率                                          | 代码调用 predict_proba(X)[:, 1]                                     | 通过   |
| TC010      | 整体评价指标   | 计算 valid/test 的 AUC 和 PR-AUC                         | 真实标签和预测概率                                                    | 输出 sample_count、positive_count、positive_rate、auc、pr_auc       | 代码已实现 evaluate_auc_metrics                                     | 通过   |
| TC011      | Top 比例指标   | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率          | 真实标签、预测概率、top_rates                                         | 输出 top_rate、top_n、top_precision、top_recall                     | 代码已实现 evaluate_top_rates，并使用 nlargest                      | 通过   |
| TC012      | 预测结果输出   | 保存 ID 字段、真实标签和 buy_probability                 | valid/test 原始数据与预测概率                                         | 生成 purchase_probability_predictions_with_path.csv                 | 代码已实现 build_prediction_result 并合并 valid/test                | 通过   |
| TC013      | 特征重要性输出 | 输出 Top50 特征重要性                                    | 训练后的模型和 feature_columns                                        | 生成 feature_importance_with_path.csv，包含 feature、coef、abs_coef | 代码已实现 get_feature_importance                                   | 通过   |
| TC014      | 结果文件保存   | 保存模型、指标、Top指标、特征重要性和预测结果            | 模型与结果表                                                          | 输出 with_path 版本文件，避免覆盖旧版结果                           | 配置文件输出文件名均带 with_path                                    | 通过   |
| TC015      | 运行入口       | 运行 python run_purchase_model.py                        | PURCHASE_MODEL_CONFIG                                                 | 打印训练完成、特征数量、数据集形状和输出文件路径                    | 入口脚本已实现对应打印逻辑                                          | 通过   |

从测试用例结果看，当前大部分测试可以通过代码结构直接确认已经实现。需要依赖真实宽表运行的测试主要是输入文件读取和模型训练，这两项需要在本地项目目录中执行 `python run_purchase_model.py` 后确认。如果本地宽表路径正确，并且 68 字段宽表包含 3 个新增路径特征，则这两项应当可以通过。

## 11. 输出文件测试

| 输出文件                                       | 说明                                          |
|:-----------------------------------------------|:----------------------------------------------|
| purchase_probability_model_with_path.joblib    | 新增行为路径特征版本的模型文件                |
| model_metrics_with_path.csv                    | valid/test 的 AUC、PR-AUC、样本数、正样本率   |
| top_rate_metrics_with_path.csv                 | Top5%、Top10%、Top20% 的真实购买率和召回率    |
| feature_importance_with_path.csv               | 逻辑回归系数与 Top50 特征重要性               |
| purchase_probability_predictions_with_path.csv | valid/test 的 ID 字段、真实标签和预测购买概率 |

输出文件设计完整，且文件名都带有 `with_path`，能够与旧版 65 字段模型结果区分。模型运行成功后，需要检查输出目录中是否生成上述 5 个文件，并进一步检查 CSV 文件字段是否完整。

建议重点检查以下字段：

```text
model_metrics_with_path.csv:
split, sample_count, positive_count, positive_rate, auc, pr_auc

top_rate_metrics_with_path.csv:
split, top_rate, top_n, top_precision, top_recall

feature_importance_with_path.csv:
feature, coef, abs_coef

purchase_probability_predictions_with_path.csv:
dataset_type, snapshot_date, user_id, item_id, item_category, label_buy_7d, buy_probability
```

## 12. 运行入口测试

运行入口脚本 `run_purchase_model.py` 的设计比较清晰，只负责导入配置和统一接口，然后启动完整流程。运行命令为：

```bash
python run_purchase_model.py
```

运行成功后，程序应打印：

```text
购买概率模型训练完成！
特征数量：...
训练集形状：...
验证集形状：...
测试集形状：...

输出文件位置：
model_path: ...
metrics_path: ...
top_rate_path: ...
feature_importance_path: ...
prediction_path: ...
```

如果宽表缺少新增行为路径特征，程序应在字段检查阶段报错，提示缺少对应字段。这种报错是符合预期的，因为它说明程序成功阻止了错误数据进入模型。

## 13. 异常处理测试

当前代码包含以下异常处理逻辑：

第一，如果输入宽表缺少 `dataset_type`、`label_buy_7d` 或 3 个新增行为路径特征，程序会抛出 `ValueError`，提示缺少必要字段。

第二，如果自动筛选后没有任何可建模的数值型特征，程序会抛出 `ValueError`，提示没有找到可用于训练的数值型特征。

第三，如果 train、valid 或 test 中任意一个数据集为空，程序会抛出 `ValueError`，提示检查 `dataset_type` 是否包含对应取值。

第四，如果某个数据集的标签只有单一类别，AUC 和 PR-AUC 会返回 NaN，避免指标计算阶段直接崩溃。

这些异常处理能够提高程序稳定性，也方便定位数据准备阶段的问题。

## 14. 时间复杂度与性能测试

| 步骤             | 时间复杂度   | 说明                                                         |
|:-----------------|:-------------|:-------------------------------------------------------------|
| 读取新版宽表     | O(n * d)     | 读取 68 字段样本数据                                         |
| 新增字段检查     | O(c)         | c 为必要字段数量，本版本检查 dataset、target 和 3 个路径特征 |
| 特征选择         | O(d)         | 选择数值型特征并排除非建模字段                               |
| 特征数值转换     | O(n * d)     | 将特征转数值型并按需转 float32                               |
| 缺失值填充       | O(n * d)     | 使用中位数填充                                               |
| 标准化           | O(n * d)     | 对特征矩阵标准化                                             |
| SGD 逻辑回归训练 | O(T * n * d) | T 为迭代轮数，每轮线性扫描样本                               |
| 预测概率         | O(m * d)     | m 为 valid/test 样本数                                       |
| AUC / PR-AUC     | O(m log m)   | 排序类评价指标需要按概率排序                                 |
| Top 比例评估     | O(m log k)   | 使用 nlargest 取 TopK，避免完整排序                          |
| 特征重要性 TopN  | O(d log N)   | 只输出前 N 个重要特征                                        |

本版本虽然新增了 3 个行为路径特征，但整体复杂度形式没有改变。设样本数为 `n`，特征数量为 `d`，模型迭代轮数为 `T`，验证集或测试集样本数为 `m`，TopK 样本数量为 `k`，训练阶段主要复杂度仍然是：

```text
O(T * n * d)
```

新增 3 个路径特征会让 `d` 从旧版约 65 字段对应的特征数量增加到新版 68 字段对应的特征数量，但由于只增加 3 个字段，整体训练成本增加有限。

Top 比例评估仍然使用 `nlargest` 获取概率最高的 TopK 样本，不进行完整排序，因此复杂度为：

```text
O(m log k)
```

相比完整排序的：

```text
O(m log m)
```

更适合只关注高概率样本的业务场景。

## 15. 测试中发现的问题

第一，当前测试材料只有代码和说明文档，没有上传真实 68 字段宽表，因此无法直接验证模型是否能在当前环境中完整跑通，也无法给出实际 AUC、PR-AUC 和 Top10% 购买率。

第二，配置文件使用相对路径读取宽表，因此本地运行前必须确认 `ml_feature_wide_table_with_path.csv` 已经放在配置指定目录中。如果文件位置不一致，需要先修改 `data_path`。

第三，当前代码没有记录训练耗时和预测耗时。如果后续需要做性能测试，建议在训练前后增加计时，并将训练耗时、预测耗时和总耗时输出到日志或指标文件中。

第四，新增路径特征虽然被强制检查是否存在，但还需要在实际运行后的特征重要性文件中观察它们的排名和系数，才能判断它们对模型是否真的有贡献。

## 16. 改进建议

首先，建议运行模型后检查 `feature_importance_with_path.csv`，确认 `pre_buy_behavior_count`、`purchase_count` 和 `pre_buy_behavior_per_purchase` 是否出现在重要特征中，并分析它们的系数方向和影响强度。

其次，建议保留旧版 65 字段模型和新版 68 字段模型的指标文件，对比 AUC、PR-AUC、Top5%、Top10%、Top20% 真实购买率和召回率，判断新增行为路径特征是否带来效果提升。

再次，建议补充运行时间统计，尤其是训练耗时和预测耗时。新增 3 个特征后，虽然理论上成本增加较小，但仍然应该用实际运行时间验证。

最后，建议在正式报告中加入新版和旧版对比表，例如：

```text
旧版模型：AUC、PR-AUC、Top10%购买率
新版模型：AUC、PR-AUC、Top10%购买率
提升幅度：新版 - 旧版
```

这样可以更直观地说明新增行为路径特征的价值。

## 17. 测试结论

综合本次测试结果，新增行为路径特征版本的购买概率模型代码封装基本符合项目要求。配置文件中已经明确声明 3 个新增行为路径字段，核心代码能够在字段检查阶段验证这些字段是否存在，并在特征选择阶段确认它们是否进入模型。模型训练、概率预测、AUC/PR-AUC 评估、Top 比例评估、特征重要性输出和结果保存流程也保持完整。

从静态检查角度看，本版本测试结论为：配置文件测试通过，新增行为路径字段检查测试通过，核心函数封装测试通过，模型 Pipeline 测试通过，TopK 评估优化测试通过，输出文件设计测试通过。由于当前没有上传真实宽表和运行结果，模型训练结果和实际指标测试需要在本地运行后进一步补充。
