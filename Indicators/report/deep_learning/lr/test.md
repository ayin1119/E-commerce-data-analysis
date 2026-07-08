# 购买概率模型代码封装测试文档

## 1. 文档说明

本文档用于测试“购买概率模型代码封装与时间复杂度优化”模块。测试对象包括配置文件 `config.py`、核心封装文件 `purchase_probability_pipeline.py`、运行入口文件 `run_purchase_model.py` 和时间复杂度说明文档。本文档根据当前上传代码进行静态检查和流程测试设计，重点验证代码结构、接口定义、参数配置、异常处理、模型 Pipeline、输出文件设计和复杂度优化是否符合项目要求。

由于本次只上传了代码文件和说明文档，没有上传真实特征宽表和模型运行结果文件，因此本文档中的“实际 AUC、PR-AUC、Top 命中率、预测概率范围”等必须依赖真实数据运行后补充。当前测试结论主要针对代码封装本身。

## 2. 测试对象

| 文件类型       | 文件名                              | 是否存在   | 大小         |
|:---------------|:------------------------------------|:-----------|:-------------|
| 配置文件       | config(3).py                        | 是         | 1,694 bytes  |
| 核心封装代码   | purchase_probability_pipeline(2).py | 是         | 12,443 bytes |
| 时间复杂度说明 | README_时间复杂度说明(2).md         | 是         | 4,471 bytes  |
| 运行入口脚本   | run_purchase_model(2).py            | 是         | 561 bytes    |

## 3. 项目功能概述

本模块用于训练用户未来 7 天购买概率模型。模型目标字段为 `label_buy_7d`，其中 1 表示未来 7 天购买，0 表示未来 7 天未购买。模型输出字段为 `buy_probability`，表示用户对某个商品在未来 7 天内发生购买的概率。

封装后的主流程如下：

```text
读取数据
→ 检查必要字段
→ 自动选择数值型特征
→ 排除 ID、日期、标签等非建模字段
→ 优化特征数据类型
→ 划分 train / valid / test
→ 构建 Pipeline 模型
→ 训练 SGD 逻辑回归模型
→ 输出 valid / test 购买概率
→ 计算 AUC、PR-AUC
→ 计算 Top5%、Top10%、Top20% 命中效果
→ 输出特征重要性
→ 保存模型和结果文件
```

## 4. 测试环境

| 环境项 | 内容 |
|---|---|
| 开发语言 | Python |
| 主要依赖库 | pandas、numpy、scikit-learn、joblib |
| 模型类型 | SGD 逻辑回归概率模型 |
| 模型实现 | `SGDClassifier(loss="log_loss")` |
| 封装方式 | 函数封装 + 配置文件驱动 + 统一运行入口 |
| 测试方式 | 静态代码检查、接口测试设计、流程测试设计、复杂度检查 |

## 5. 配置文件测试

### 5.1 配置项检查

| 配置项             | 配置值                                                                        |
|:-------------------|:------------------------------------------------------------------------------|
| 输入宽表路径       | ../../../../form/deep_learning/with_path/mml_feature_wide_table_with_path.csv |
| 输出目录           | ../../../../form/deep_learning/with_path                                      |
| 数据集字段         | dataset_type                                                                  |
| 训练/验证/测试标识 | train / valid / test                                                          |
| 目标标签           | label_buy_7d                                                                  |
| 不进入模型字段     | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d    |
| 预测结果保留字段   | dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d    |
| 模型参数           | random_state=42, max_iter=1000, tol=0.001, class_weight=balanced              |
| 是否使用 float32   | True                                                                          |
| Top 比例           | 5%、10%、20%                                                                  |
| 特征重要性输出数量 | 50                                                                            |
| 模型输出文件名     | purchase_probability_model.joblib                                             |
| 指标输出文件名     | model_metrics.csv                                                             |
| Top 指标输出文件名 | top_rate_metrics.csv                                                          |
| 特征重要性文件名   | feature_importance.csv                                                        |
| 预测结果文件名     | purchase_probability_predictions.csv                                          |

配置文件中已经将输入路径、输出目录、数据集划分字段、目标字段、非建模字段、模型参数、Top 比例和输出文件名集中管理。这样做的优点是后续更换数据路径、调整模型参数或修改输出文件名时，不需要直接修改核心训练代码。

### 5.2 配置测试结论

配置文件整体结构清晰，关键配置项完整。`drop_columns` 中排除了 `dataset_type`、`snapshot_date`、`user_id`、`item_id`、`item_category` 和 `label_buy_7d`，可以避免 ID、日期、标签等字段错误进入模型。`top_rates` 配置为 5%、10% 和 20%，符合后续业务排序评估需求。`use_float32=True`，可以降低特征矩阵内存占用。

## 6. 核心函数接口测试

| 函数名                         | 是否存在   | 测试目的                                        |
|:-------------------------------|:-----------|:------------------------------------------------|
| load_data                      | 是         | 读取配置中的特征宽表                            |
| check_required_columns         | 是         | 检查 dataset_col 和 target_col 是否存在         |
| get_feature_columns            | 是         | 自动选择数值型特征并排除非建模字段              |
| optimize_memory                | 是         | 将特征转为数值型，按配置转 float32，标签转 int8 |
| split_dataset                  | 是         | 按 train、valid、test 划分数据集并检查空集      |
| make_xy                        | 是         | 拆分特征矩阵 X 和标签 y                         |
| build_model                    | 是         | 构建 imputer + scaler + SGDClassifier Pipeline  |
| train_model                    | 是         | 训练购买概率模型                                |
| predict_probability            | 是         | 输出购买概率                                    |
| evaluate_auc_metrics           | 是         | 计算样本数、正样本率、AUC、PR-AUC               |
| evaluate_top_rates             | 是         | 计算 Top5%、Top10%、Top20% 命中效果             |
| build_prediction_result        | 是         | 保存 ID 字段、真实标签和预测概率                |
| get_feature_importance         | 是         | 提取逻辑回归系数并输出 TopN 特征                |
| save_outputs                   | 是         | 保存模型、指标、Top 指标、特征重要性和预测结果  |
| run_purchase_probability_model | 是         | 封装完整训练、预测、评估、保存流程              |

从函数检查结果看，核心封装代码已经覆盖了完整的建模流程。每个函数职责相对独立，便于单独测试，也便于后续维护和扩展。其中，`run_purchase_probability_model(config)` 是统一入口，外部只需要传入配置字典，就可以完成从读取数据到保存模型结果的完整流程。

## 7. 静态检查结果

| 编号   | 检查项           | 检查方法                                                                                             | 预期结果                                    | 实际结果                                                                                                 | 结论   |
|:-------|:-----------------|:-----------------------------------------------------------------------------------------------------|:--------------------------------------------|:---------------------------------------------------------------------------------------------------------|:-------|
| SC001  | 配置文件是否存在 | 读取 config(3).py                                                                                    | 可以读取 PURCHASE_MODEL_CONFIG              | 已成功解析 PURCHASE_MODEL_CONFIG                                                                         | 通过   |
| SC002  | 必要配置项完整性 | 检查 data_path、output_dir、dataset_col、target_col、drop_columns、id_columns、top_rates、输出文件名 | 关键配置项均存在                            | 关键配置项完整                                                                                           | 通过   |
| SC003  | 非建模字段排除   | 检查 drop_columns                                                                                    | ID、日期、标签字段不进入模型                | drop_columns 包含 dataset_type、snapshot_date、user_id、item_id、item_category、label_buy_7d             | 通过   |
| SC004  | 核心函数完整性   | 解析 purchase_probability_pipeline(2).py 中的函数定义                                                | 完整包含从读取数据到保存输出的全部函数      | 共检测到 15 个函数，必要函数缺失：无                                                                     | 通过   |
| SC005  | 模型结构         | 检查 build_model 中是否包含 SimpleImputer、StandardScaler、SGDClassifier                             | Pipeline 包含缺失值填充、标准化和分类器     | 代码中包含 SimpleImputer、StandardScaler、SGDClassifier                                                  | 通过   |
| SC006  | 概率模型设置     | 检查 SGDClassifier 参数                                                                              | loss='log_loss'，class_weight 使用 balanced | SGDClassifier 使用 loss='log_loss'，class_weight 从配置读取，默认 balanced                               | 通过   |
| SC007  | 内存优化         | 检查 optimize_memory 函数和 use_float32 配置                                                         | 特征列可转为 float32，标签转 int8           | 代码中支持 float32，目标标签转 int8                                                                      | 通过   |
| SC008  | Top 比例评估优化 | 检查 evaluate_top_rates 是否使用 nlargest                                                            | 使用 TopK 思路，不做完整排序                | 代码中使用 prob.nlargest(top_n)                                                                          | 通过   |
| SC009  | 特征重要性输出   | 检查 get_feature_importance 是否提取 coef_ 并按 abs_coef 输出                                        | 输出 feature、coef、abs_coef                | 代码中提取 clf.coef_[0]，并计算 abs_coef                                                                 | 通过   |
| SC010  | 运行入口         | 检查 run_purchase_model(2).py                                                                        | 入口脚本调用统一接口并打印输出信息          | 入口脚本调用 run_purchase_probability_model(PURCHASE_MODEL_CONFIG)，并打印特征数量、数据集形状和输出路径 | 通过   |

静态检查结果表明，当前代码封装结构基本完整，关键函数、模型结构、参数配置、TopK 优化和输出文件设计均已实现。需要注意的是，静态检查只能说明代码结构和逻辑设计符合要求，不能替代真实数据运行测试。后续仍需要在本地真实宽表路径下运行 `python run_purchase_model.py`，确认模型能够完整训练并输出结果文件。

## 8. 测试用例设计与执行结果

| 用例编号   | 测试模块     | 测试内容                                               | 测试输入                                       | 预期结果                                                      | 实际结果                                                    | 结论   |
|:-----------|:-------------|:-------------------------------------------------------|:-----------------------------------------------|:--------------------------------------------------------------|:------------------------------------------------------------|:-------|
| TC001      | 数据读取     | 使用配置文件中的 data_path 读取特征宽表                | ml_feature_wide_table_with_path.csv            | 能够正常读取 DataFrame                                        | 需在本地真实数据路径下运行验证                              | 待执行 |
| TC002      | 字段检查     | 检查 dataset_type 和 label_buy_7d 是否存在             | 包含必要字段的宽表                             | 字段存在时正常通过；字段缺失时抛出 ValueError                 | 代码已实现缺失字段检查逻辑                                  | 通过   |
| TC003      | 特征选择     | 自动选择数值型特征，并排除 ID、日期、标签等字段        | 含数值特征和非建模字段的宽表                   | 输出 feature_columns，且不包含 drop_columns                   | 代码已实现 select_dtypes 和 drop_columns 过滤               | 通过   |
| TC004      | 内存优化     | 将特征列转为 float32，将标签列转为 int8                | 原始特征列                                     | 特征可转为数值型，内存占用降低                                | 代码已实现 to_numeric、float32 和 int8 转换                 | 通过   |
| TC005      | 数据集划分   | 根据 dataset_type 划分 train、valid、test              | dataset_type 包含 train、valid、test 的宽表    | 返回三个非空数据集                                            | 代码已实现空集检查，空集时抛出 ValueError                   | 通过   |
| TC006      | 模型构建     | 构建购买概率模型 Pipeline                              | 配置参数                                       | Pipeline 包含 imputer、scaler、clf 三个步骤                   | 代码中已构建 SimpleImputer + StandardScaler + SGDClassifier | 通过   |
| TC007      | 模型训练     | 使用训练集训练 SGD 逻辑回归模型                        | X_train、y_train                               | 模型训练完成，后续可调用 predict_proba                        | 需在本地真实数据路径下运行验证                              | 待执行 |
| TC008      | 概率预测     | 对 valid/test 输出 buy_probability                     | 训练后的模型和 X_valid/X_test                  | 输出 0 到 1 之间的购买概率                                    | 代码已调用 predict_proba(X)[:, 1]                           | 通过   |
| TC009      | 模型评价     | 计算 AUC 和 PR-AUC                                     | 真实标签 y_true 和预测概率 pred_prob           | 输出 sample_count、positive_count、positive_rate、auc、pr_auc | 代码已实现 evaluate_auc_metrics，且对单一标签情况返回 NaN   | 通过   |
| TC010      | Top比例评估  | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率        | 真实标签 y_true、预测概率 pred_prob、top_rates | 输出 top_rate、top_n、top_precision、top_recall               | 代码已实现 evaluate_top_rates，并使用 nlargest 优化         | 通过   |
| TC011      | 预测结果保存 | 保存 ID 字段、真实标签和预测概率                       | valid/test 原始数据和预测概率                  | 输出 purchase_probability_predictions.csv                     | 代码已实现 build_prediction_result 和 concat valid/test     | 通过   |
| TC012      | 特征重要性   | 提取模型系数并输出 TopN 重要特征                       | 训练后的模型和 feature_columns                 | 输出 feature、coef、abs_coef                                  | 代码已实现 get_feature_importance                           | 通过   |
| TC013      | 文件输出     | 保存模型、指标、Top指标、特征重要性和预测结果          | 模型与各类结果表                               | 输出 joblib 和 4 个 csv 文件                                  | 代码已实现 save_outputs，并按配置文件名保存                 | 通过   |
| TC014      | 统一接口     | 调用 run_purchase_probability_model(config) 完成全流程 | PURCHASE_MODEL_CONFIG                          | 返回输出路径、特征数量和数据集形状                            | 代码已实现统一接口并返回 outputs                            | 通过   |

从测试用例看，除“数据读取”和“模型训练”必须依赖真实宽表运行外，其余大部分功能都可以通过代码结构确认已经实现。正式提交时，可以在本地运行成功后，将 TC001 和 TC007 的结论从“待执行”改为“通过”，并补充实际训练输出的特征数量、训练集形状、验证集形状、测试集形状和输出文件路径。

## 9. 输出文件测试

| 输出文件                             | 说明                                                 |
|:-------------------------------------|:-----------------------------------------------------|
| purchase_probability_model.joblib    | 训练好的购买概率模型                                 |
| model_metrics.csv                    | valid/test 的样本数、正样本数、正样本率、AUC、PR-AUC |
| top_rate_metrics.csv                 | Top5%、Top10%、Top20% 的命中效果                     |
| feature_importance.csv               | 逻辑回归系数和影响强度排名                           |
| purchase_probability_predictions.csv | 验证集和测试集的预测购买概率                         |

输出文件设计较完整，能够覆盖模型保存、整体指标、Top 比例指标、特征重要性和预测结果。运行成功后，应检查输出目录下是否生成以上 5 个文件，并进一步检查 CSV 文件是否能够正常打开、字段是否完整、是否存在空值和异常值。

## 10. 异常处理测试

当前代码中已经包含以下异常处理逻辑：

第一，`check_required_columns` 会检查数据集中是否存在 `dataset_col` 和 `target_col`。如果必要字段缺失，会抛出 `ValueError`，提示用户检查输入宽表字段。

第二，`get_feature_columns` 会自动选择数值型特征并排除非建模字段。如果没有找到可用于训练的数值型特征，会抛出 `ValueError`。

第三，`split_dataset` 会检查训练集、验证集和测试集是否为空。如果 `dataset_type` 中缺少 train、valid 或 test，对应数据集为空时会抛出 `ValueError`。

第四，`evaluate_auc_metrics` 对单一类别标签进行了处理。当某个数据集的标签只有 0 或只有 1 时，AUC 和 PR-AUC 返回 NaN，避免程序直接报错。

这些异常处理可以提高程序运行稳定性，也有助于定位数据准备过程中的问题。

## 11. 时间复杂度与性能测试

| 步骤             | 时间复杂度   | 说明                                |
|:-----------------|:-------------|:------------------------------------|
| 读取数据         | O(n * d)     | 读取样本和特征宽表                  |
| 特征数值转换     | O(n * d)     | 将特征转为数值型                    |
| 缺失值填充       | O(n * d)     | 使用中位数填充缺失值                |
| 标准化           | O(n * d)     | 对所有特征进行标准化                |
| SGD 逻辑回归训练 | O(T * n * d) | 每轮线性扫描训练样本                |
| 预测概率         | O(m * d)     | 对验证集和测试集输出概率            |
| AUC / PR-AUC     | O(m log m)   | 排序类评价指标需要按概率排序        |
| Top 比例评估     | O(m log k)   | 使用 nlargest 取 TopK，避免完整排序 |
| 特征重要性 TopN  | O(d log N)   | 只输出前 N 个重要特征               |

从复杂度角度看，训练阶段主要复杂度为：

```text
O(T * n * d)
```

其中 `T` 是模型迭代轮数，`n` 是训练样本数，`d` 是特征数量。由于本项目使用 `SGDClassifier(loss="log_loss")`，每轮训练只需要线性扫描样本，因此适合较大规模的特征宽表训练。

Top 比例评估使用 `nlargest` 获取概率最高的前 K 个样本，而不是对全部预测结果完整排序，因此 TopK 评估复杂度由：

```text
O(m log m)
```

优化为：

```text
O(m log k)
```

其中 `m` 是验证集或测试集样本数，`k` 是 TopK 样本数量。该优化适合推荐排序和营销触达场景，因为业务通常只关心预测概率最高的一部分样本。

空间复杂度主要来自特征矩阵，理论上为：

```text
O(n * d)
```

代码中支持将特征转为 `float32`，使实际内存占用从约 `O(n * d * 8)` 降低到约 `O(n * d * 4)`，对大规模数据更友好。

## 12. 运行入口测试

运行入口文件 `run_purchase_model.py` 的作用是导入配置文件和统一接口，然后调用完整训练流程。运行命令如下：

```bash
python run_purchase_model.py
```

运行成功后，程序应输出以下信息：

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

该运行入口设计清晰，便于用户直接执行完整流程，也便于在实验报告中记录模型训练结果。

## 13. 测试中发现的问题

第一，配置文件中的输入路径为相对路径，且文件名写作 `mml_feature_wide_table_with_path.csv`。如果本地真实文件名是 `ml_feature_wide_table_with_path.csv`，则运行时会出现找不到文件的问题。因此运行前需要确认宽表文件名和路径是否完全一致。

第二，当前代码没有记录训练耗时和预测耗时。虽然 README 中说明了时间复杂度优化，但如果要在测试文档中体现实际性能，建议在 `run_purchase_probability_model` 中增加计时统计，例如记录数据读取耗时、训练耗时、预测耗时和总耗时。

第三，当前模型使用的是线性模型 `SGDClassifier(loss="log_loss")`。它训练速度快、解释性较强，但对非线性关系的表达能力有限。后续如果追求更高预测效果，可以在同一封装结构下替换为 LightGBM、RandomForest 或 XGBoost 等模型进行对比。

第四，当前测试文档基于代码文件进行静态检查，没有真实运行宽表，因此无法给出实际 AUC、PR-AUC、Top10% 购买率、预测概率范围和预测结果完整性。正式提交时需要在本地运行后补充这些结果。

## 14. 改进建议

首先，建议在配置文件中再次确认 `data_path` 是否指向正确的宽表文件，避免因为路径或文件名错误导致程序无法读取数据。

其次，建议增加运行耗时统计，在输出结果中增加 `train_time_seconds`、`predict_time_seconds` 和 `total_time_seconds`，这样测试文档可以更完整地说明代码优化效果。

再次，建议增加预测结果校验逻辑，例如检查 `buy_probability` 是否全部在 0 到 1 之间，检查预测结果是否存在缺失值和重复行，检查 valid/test 的正样本率是否符合预期。

最后，建议保留当前封装结构，将模型训练流程做成可复用模块。后续无论是更换样本比例、增加路径特征、做特征筛选，还是替换模型算法，都可以在当前框架基础上继续扩展。

## 15. 测试结论

综合本次测试结果，购买概率模型代码封装基本符合项目要求。配置文件能够集中管理路径、字段、模型参数和输出文件名；核心代码已经完成数据读取、字段检查、特征选择、内存优化、数据集划分、模型训练、概率预测、指标评估、Top 比例评估、特征重要性输出和结果保存；运行入口文件可以调用统一接口完成完整流程。

从代码结构和静态检查角度看，本模块测试结论为：配置文件测试通过，接口封装测试通过，模型 Pipeline 测试通过，TopK 评估优化测试通过，输出文件设计测试通过。由于本次没有上传真实宽表和运行结果，数据读取测试和模型训练结果测试需要在本地运行后进一步确认。
