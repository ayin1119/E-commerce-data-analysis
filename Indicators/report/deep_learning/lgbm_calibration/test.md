# LightGBM 概率校准测试文档

## 1. 文档说明

本文档用于测试 “LightGBM 概率校准工程”。该工程接收 LightGBM 最优模型输出的购买概率结果，对原始概率进行校准，并比较原始概率、Platt Scaling 校准概率和 Isotonic Regression 校准概率在排序能力、概率准确性和 Top 比例命中效果上的差异。

本次上传的文件包括概率校准配置文件、核心校准代码、README 说明和运行入口脚本。由于本次没有上传 `lgbm_predictions_best_with_path.csv` 和校准运行后的结果文件，因此本文档重点进行配置测试、代码流程测试、校准方法测试、输出文件测试和复杂度分析。实际校准后的 AUC、PR-AUC、Brier Score、Log Loss、ECE、MCE 和 Top10% 购买率需要在本地运行后补充。

## 2. 测试对象

| 文件类型         | 文件名                         | 是否存在   | 文件大小    |
|:-----------------|:-------------------------------|:-----------|:------------|
| 概率校准配置文件 | config_lgbm_calibration.py     | 是         | 975 bytes   |
| 概率校准核心代码 | lgbm_calibration.py            | 是         | 8,204 bytes |
| 概率校准说明文档 | README_LightGBM概率校准说明.md | 是         | 774 bytes   |
| 运行入口脚本     | run_lgbm_calibration.py        | 是         | 304 bytes   |

## 3. 模块背景

LightGBM 模型输出的是用户未来 7 天购买某个商品的概率。模型的排序效果可以通过 AUC、PR-AUC 和 Top 比例指标评价，但模型输出的概率本身未必等于真实购买率。例如，模型预测一批样本购买概率平均为 0.60，但真实购买率可能只有 0.45，这说明概率存在偏高或偏低的问题。

概率校准的目标是让模型输出的概率更接近真实发生率，使概率结果更适合解释和决策。本工程使用两种常见校准方法：

```text
Platt Scaling
Isotonic Regression
```

其中，Platt Scaling 使用逻辑回归对原始概率的 logit 值进行校准，方法相对稳定；Isotonic Regression 是非参数单调校准方法，拟合能力更强，但在样本较少时更容易过拟合。

## 4. 测试目标

本次测试主要验证以下内容：

第一，检查配置文件是否正确设置输入预测文件、输出目录、字段名、校准分箱数量、Top 评估比例和输出文件名。

第二，检查代码是否能够读取 LightGBM 最优模型预测结果，并验证 `dataset_type`、`label_buy_7d`、`lgbm_probability` 三个必要字段。

第三，检查代码是否能用 valid 集拟合 Platt Scaling 和 Isotonic Regression 校准器，并在 valid/test 上生成校准后概率。

第四，检查代码是否能同时评估 original、platt、isotonic 三种概率方法的 AUC、PR-AUC、Brier Score、Log Loss、ECE、MCE 和平均预测概率。

第五，检查代码是否能够生成 10 分箱校准报告，分析每个概率区间的平均预测概率与真实购买率之间的差距。

第六，检查代码是否能够对三种概率方法分别计算 Top5%、Top10%、Top20% 的真实购买率和召回率。

第七，检查校准后预测结果、指标文件、分箱报告、Top 比例报告和校准器文件是否能够正常保存。

## 5. 测试环境

| 环境项 | 内容 |
|---|---|
| 开发语言 | Python |
| 主要依赖库 | pandas、numpy、scikit-learn、joblib |
| 校准方法 | Platt Scaling、Isotonic Regression |
| 输入文件 | `lgbm_predictions_best_with_path.csv` |
| 输入概率字段 | `lgbm_probability` |
| 目标字段 | `label_buy_7d` |
| 数据集划分 | valid 用于拟合校准器，test 用于评估校准效果 |
| 测试方式 | 静态代码检查 + 流程测试设计 |

## 6. 配置文件测试

### 6.1 配置项检查

| 配置项             | 配置值                                                                            |
|:-------------------|:----------------------------------------------------------------------------------|
| 输入预测结果路径   | ../../../../form/deep_learning/with_path/lgbm/lgbm_predictions_best_with_path.csv |
| 输出目录           | ../../../../form/deep_learning/with_path/lgbm_calibration                         |
| 数据集字段         | dataset_type                                                                      |
| 验证集标识         | valid                                                                             |
| 测试集标识         | test                                                                              |
| 目标标签字段       | label_buy_7d                                                                      |
| 原始概率字段       | lgbm_probability                                                                  |
| 校准分箱数量       | 10                                                                                |
| Top 评估比例       | 5%、10%、20%                                                                      |
| 校准后预测结果文件 | calibrated_lgbm_predictions_with_path.csv                                         |
| 校准指标文件       | lgbm_calibration_metrics_with_path.csv                                            |
| 分箱校准报告文件   | lgbm_calibration_bin_report_with_path.csv                                         |
| Top 比例指标文件   | lgbm_calibration_top_rate_metrics_with_path.csv                                   |
| 校准器文件         | lgbm_probability_calibrators_with_path.joblib                                     |

### 6.2 配置测试结论

配置文件整体结构完整，已经明确设置输入预测文件路径、输出目录、数据集字段、目标字段、原始概率字段、分箱数量、Top 评估比例和输出文件名。配置中使用 `valid` 作为校准器拟合数据集，使用 `test` 作为校准效果评估数据集，符合模型校准的一般流程。输出文件名均带有 `with_path`，可以与前一阶段 LightGBM 模型结果保持一致。

## 7. 核心函数接口测试

| 函数名                     | 是否存在   | 测试说明                                                               |
|:---------------------------|:-----------|:-----------------------------------------------------------------------|
| resolve_path               | 是         | 将配置中的相对路径转换为基于当前文件的绝对路径                         |
| logit                      | 是         | 对概率进行裁剪后转换为 logit，用于 Platt Scaling                       |
| expected_calibration_error | 是         | 按概率区间计算 ECE、MCE 和分箱校准明细                                 |
| evaluate_top_rates         | 是         | 计算 Top5%、Top10%、Top20% 的真实购买率和召回率                        |
| run_lgbm_calibration       | 是         | 统一执行读取预测结果、拟合校准器、生成校准概率、评估指标并保存输出文件 |

核心代码函数数量不多，但覆盖了概率校准的关键流程。`run_lgbm_calibration(config)` 是统一入口，负责读取预测结果、检查字段、清洗概率、拟合校准器、生成校准概率、评估指标、生成分箱报告、计算 Top 比例指标并保存输出文件。

## 8. 概率校准流程测试

本模块完整校准流程如下：

```text
读取 lgbm_predictions_best_with_path.csv
→ 检查 dataset_type、label_buy_7d、lgbm_probability
→ 将标签转为整数
→ 将 lgbm_probability 转为数值并裁剪到 [1e-6, 1 - 1e-6]
→ 划分 valid 和 test
→ 使用 valid 原始概率拟合 Platt Scaling
→ 使用 valid 原始概率拟合 Isotonic Regression
→ 对 valid/test 生成 original、platt、isotonic 三种概率
→ 对三种概率分别计算 AUC、PR-AUC、Brier Score、Log Loss、ECE、MCE
→ 生成 10 分箱校准报告
→ 计算 Top5%、Top10%、Top20% 命中效果
→ 保存校准预测结果、指标文件、分箱报告、Top 指标和校准器
```

该流程中，valid 集用于拟合校准器，test 集用于观察校准器在未参与拟合数据上的效果。这样可以避免只在拟合集上评价校准效果造成结果偏乐观。

## 9. 静态检查结果

| 编号   | 检查项                 | 检查方法                                                      | 预期结果                                                        | 实际结果                                                                                                          | 结论   |
|:-------|:-----------------------|:--------------------------------------------------------------|:----------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------|:-------|
| SC001  | 配置字典解析           | 解析 LGBM_CALIBRATION_CONFIG                                  | 配置字典能够正常解析                                            | 已成功解析配置字典                                                                                                | 通过   |
| SC002  | 输入预测文件配置       | 检查 prediction_path                                          | 输入为 LightGBM 最优模型预测结果                                | ../../../../form/deep_learning/with_path/lgbm/lgbm_predictions_best_with_path.csv                                 | 通过   |
| SC003  | 关键字段配置           | 检查 dataset_col、target_col、probability_col                 | 包含 dataset_type、label_buy_7d、lgbm_probability               | dataset_type、label_buy_7d、lgbm_probability                                                                      | 通过   |
| SC004  | 校准方法               | 检查核心代码是否包含 LogisticRegression 和 IsotonicRegression | 同时支持 Platt Scaling 和 Isotonic Regression                   | 代码包含 LogisticRegression 和 IsotonicRegression                                                                 | 通过   |
| SC005  | Platt Scaling 输入处理 | 检查 logit 函数和 platt.fit                                   | 对原始概率做 logit 变换后拟合逻辑回归校准器                     | 代码对 valid_prob 进行 logit 后训练 LogisticRegression                                                            | 通过   |
| SC006  | Isotonic 校准          | 检查 IsotonicRegression(out_of_bounds='clip')                 | 使用验证集原始概率拟合同分布回归校准器                          | 代码使用 IsotonicRegression(out_of_bounds='clip')                                                                 | 通过   |
| SC007  | 训练/评估数据划分      | 检查 valid_df 和 test_df                                      | valid 用于拟合校准器，test 用于评估校准效果                     | 代码用 valid 拟合 Platt 和 Isotonic，并对 valid/test 都输出校准概率                                               | 通过   |
| SC008  | 概率范围处理           | 检查 clip(1e-6, 1 - 1e-6)                                     | 避免 logit、log_loss 因 0 或 1 概率报错                         | 代码对原始概率和评估概率进行裁剪                                                                                  | 通过   |
| SC009  | 校准指标完整性         | 检查 evaluate 部分输出字段                                    | 输出 AUC、PR-AUC、Brier Score、Log Loss、ECE、MCE、平均预测概率 | 代码包含 auc、pr_auc、brier_score、log_loss、ece_10bins、mce_10bins、mean_predicted_probability                   | 通过   |
| SC010  | 分箱校准报告           | 检查 expected_calibration_error 返回 bin_df                   | 输出每个概率分箱的样本数、平均预测概率、真实购买率和绝对误差    | 代码输出 bin、prob_left、prob_right、sample_count、mean_predicted_probability、actual_purchase_rate、absolute_gap | 通过   |
| SC011  | Top 比例评估           | 检查 evaluate_top_rates 是否使用 nlargest                     | 对 original、platt、isotonic 都计算 Top5%、Top10%、Top20%       | 代码使用 prob.nlargest(top_n)，并遍历 methods 计算 Top 指标                                                       | 通过   |
| SC012  | 输出文件保存           | 检查 to_csv 和 joblib.dump                                    | 保存校准预测、校准指标、分箱报告、Top 指标和校准器              | 代码保存 4 个 CSV 文件和 1 个 joblib 校准器文件                                                                   | 通过   |
| SC013  | 运行入口               | 检查 run_lgbm_calibration.py                                  | 调用 run_lgbm_calibration(LGBM_CALIBRATION_CONFIG)              | 入口脚本调用统一接口，并打印输出文件路径                                                                          | 通过   |

静态检查结果表明，当前概率校准工程已经实现主要功能，包括输入字段检查、概率裁剪、Platt Scaling、Isotonic Regression、校准概率输出、整体指标计算、分箱校准报告、Top 比例评估和校准器保存。需要注意的是，静态检查只能说明代码逻辑完整，不能替代真实数据运行测试。

## 10. 测试用例与执行结果

| 用例编号   | 测试模块            | 测试内容                                                                           | 测试输入                            | 预期结果                                             | 实际结果                                                                                | 结论   |
|:-----------|:--------------------|:-----------------------------------------------------------------------------------|:------------------------------------|:-----------------------------------------------------|:----------------------------------------------------------------------------------------|:-------|
| TC001      | 输入文件读取        | 读取 LightGBM 最优模型预测结果                                                     | lgbm_predictions_best_with_path.csv | 文件能够正常读取为 DataFrame                         | 需在本地真实路径下运行验证                                                              | 待执行 |
| TC002      | 字段完整性          | 检查 dataset_type、label_buy_7d、lgbm_probability 是否存在                         | LightGBM 预测结果文件               | 字段完整；缺失字段时抛出 ValueError                  | 代码已实现 required_cols 和 missing_cols 检查                                           | 通过   |
| TC003      | 概率数据清洗        | 将 lgbm_probability 转为数值，并裁剪到 1e-6 到 1-1e-6                              | 原始 LightGBM 概率                  | 概率可用于 logit 和 log_loss 计算                    | 代码已实现 pd.to_numeric 和 clip                                                        | 通过   |
| TC004      | 数据集划分          | 按 dataset_type 划分 valid 和 test                                                 | 预测结果文件                        | valid 用于拟合校准器，test 用于校准效果评估          | 代码已实现 valid_df 和 test_df，并检查空集                                              | 通过   |
| TC005      | Platt Scaling       | 用 valid 集原始概率的 logit 值拟合 LogisticRegression                              | valid_prob、y_valid                 | 生成 platt_lgbm_probability                          | 代码已实现 Platt 校准流程                                                               | 通过   |
| TC006      | Isotonic Regression | 用 valid 集原始概率拟合 IsotonicRegression                                         | valid_prob、y_valid                 | 生成 isotonic_lgbm_probability                       | 代码已实现 Isotonic 校准流程                                                            | 通过   |
| TC007      | 校准后预测结果      | 对 valid/test 同时保存原始概率、Platt 概率和 Isotonic 概率                         | valid_df、test_df                   | 生成 calibrated_lgbm_predictions_with_path.csv       | 代码已实现 original_lgbm_probability、platt_lgbm_probability、isotonic_lgbm_probability | 通过   |
| TC008      | 整体指标评估        | 对 original、platt、isotonic 分别计算 AUC、PR-AUC、Brier Score、Log Loss、ECE、MCE | y_true 和三种概率                   | 生成 lgbm_calibration_metrics_with_path.csv          | 代码已实现多方法多数据集指标计算                                                        | 通过   |
| TC009      | 分箱校准报告        | 按 10 个概率区间计算平均预测概率、真实购买率和绝对误差                             | y_true、prob、n_bins=10             | 生成 lgbm_calibration_bin_report_with_path.csv       | 代码已实现 expected_calibration_error                                                   | 通过   |
| TC010      | Top比例评估         | 对 original、platt、isotonic 分别计算 Top5%、Top10%、Top20% 命中效果               | target、probability、top_rates      | 生成 lgbm_calibration_top_rate_metrics_with_path.csv | 代码已实现 evaluate_top_rates                                                           | 通过   |
| TC011      | 校准器保存          | 保存 Platt 和 Isotonic 校准器                                                      | platt、isotonic                     | 生成 lgbm_probability_calibrators_with_path.joblib   | 代码已通过 joblib.dump 保存校准器、输入概率字段、目标字段和拟合集                       | 通过   |
| TC012      | 运行入口            | 运行 python run_lgbm_calibration.py                                                | LGBM_CALIBRATION_CONFIG             | 打印 LightGBM 概率校准完成和输出文件路径             | 入口脚本已实现对应逻辑                                                                  | 通过   |

从测试用例看，除输入文件读取需要依赖真实 `lgbm_predictions_best_with_path.csv` 运行验证外，其余核心逻辑均可以通过代码结构确认已经实现。正式提交前，应在本地运行 `python run_lgbm_calibration.py`，确认所有输出文件能够正常生成。

## 11. 输出文件测试

| 输出文件                                        | 说明                                                                                                  |
|:------------------------------------------------|:------------------------------------------------------------------------------------------------------|
| calibrated_lgbm_predictions_with_path.csv       | 保存 valid/test 的原始概率、Platt 校准概率和 Isotonic 校准概率                                        |
| lgbm_calibration_metrics_with_path.csv          | 保存 original、platt、isotonic 在 valid/test 上的 AUC、PR-AUC、Brier Score、Log Loss、ECE、MCE 等指标 |
| lgbm_calibration_bin_report_with_path.csv       | 保存每种方法在每个概率分箱中的平均预测概率、真实购买率和绝对误差                                      |
| lgbm_calibration_top_rate_metrics_with_path.csv | 保存 original、platt、isotonic 在 Top5%、Top10%、Top20% 上的真实购买率和召回率                        |
| lgbm_probability_calibrators_with_path.joblib   | 保存 Platt 和 Isotonic 两个校准器，便于后续复用                                                       |

输出文件设计完整，能够同时支持概率解释、指标对比、分箱校准分析和校准器复用。其中，`calibrated_lgbm_predictions_with_path.csv` 是后续业务分析最重要的文件，因为它同时保留了原始概率、Platt 校准概率和 Isotonic 校准概率。`lgbm_calibration_metrics_with_path.csv` 用于判断哪种概率方法更适合解释，`lgbm_calibration_top_rate_metrics_with_path.csv` 用于确认校准是否影响排序场景下的 Top 样本命中效果。

## 12. 指标测试设计

本工程评估三类概率方法：

```text
original_lgbm_probability
platt_lgbm_probability
isotonic_lgbm_probability
```

主要指标如下：

| 指标 | 作用 | 越大/越小越好 |
|---|---|---|
| AUC | 衡量正负样本整体排序能力 | 越大越好 |
| PR-AUC | 衡量正样本识别能力，适合样本不均衡场景 | 越大越好 |
| Brier Score | 衡量概率预测均方误差 | 越小越好 |
| Log Loss | 衡量概率预测损失 | 越小越好 |
| ECE | 衡量预测概率与真实发生率的平均校准误差 | 越小越好 |
| MCE | 衡量所有分箱中最大的校准误差 | 越小越好 |
| Mean Predicted Probability | 平均预测概率，可与正样本率对比 | 越接近正样本率越好 |
| Top Precision | Top 样本中的真实购买率 | 越大越好 |
| Top Recall | Top 样本覆盖真实购买样本的比例 | 越大越好 |

需要注意的是，概率校准通常主要改善 Brier Score、Log Loss、ECE 和 MCE，不一定明显提高 AUC 或 PR-AUC。因为 AUC 和 PR-AUC主要取决于样本排序，而校准主要调整概率值的可信程度。

## 13. 分箱校准报告测试

本工程使用 10 个概率区间进行校准分析。每个分箱会输出：

```text
bin
prob_left
prob_right
sample_count
mean_predicted_probability
actual_purchase_rate
absolute_gap
```

其中，`mean_predicted_probability` 表示该概率区间内模型平均预测购买概率，`actual_purchase_rate` 表示该区间真实购买率，`absolute_gap` 表示两者之间的绝对差距。如果校准效果较好，各分箱中的平均预测概率应当接近真实购买率，ECE 和 MCE 应当下降。

该报告可以帮助判断模型在哪些概率区间偏高或偏低。例如，如果 0.7 到 0.8 分箱的平均预测概率为 0.75，但真实购买率只有 0.55，则说明模型在高概率区间可能过度自信。

## 14. Top 比例评估测试

本工程对 original、platt、isotonic 三种概率方法都计算 Top5%、Top10%、Top20% 指标。Top 指标主要用于排序场景，例如推荐、营销触达、重点用户筛选等。

需要注意的是，校准方法如果保持单调性，通常不会明显改变样本排序，因此 Top Precision 和 Top Recall 可能与原始概率接近。尤其 Platt Scaling 和 Isotonic Regression 都是基于概率的单调校准方法，主要目标不是改变排序，而是让概率值更接近真实发生率。因此，排序场景可以继续优先使用 `original_lgbm_probability`，概率解释场景可以优先观察 `platt_lgbm_probability` 或 `isotonic_lgbm_probability`。

## 15. 异常与风险测试

当前代码已经实现主要流程，但仍有以下风险需要注意：

第一，如果输入文件路径错误，程序会在读取 CSV 时直接报错。建议后续增加文件存在性检查，使错误提示更加明确。

第二，如果输入预测结果缺少 `dataset_type`、`label_buy_7d` 或 `lgbm_probability`，程序会抛出 `ValueError`，这是符合预期的保护逻辑。

第三，如果 valid 或 test 数据集为空，程序会抛出 `ValueError`，防止无法拟合校准器或无法评估校准效果。

第四，如果 valid 集样本量较小，Isotonic Regression 可能产生过拟合，导致 valid 上校准效果很好但 test 上不稳定。因此最终选择校准方法时，应优先观察 test 集 Brier Score、Log Loss、ECE 和 MCE。

第五，如果原始概率中存在 0 或 1，直接计算 logit 或 Log Loss 可能报错，因此代码对概率进行了裁剪，这一点已经实现。

## 16. 时间复杂度与性能测试

| 步骤                     | 时间复杂度             | 说明                                        |
|:-------------------------|:-----------------------|:--------------------------------------------|
| 读取预测结果             | O(n)                   | n 为 valid/test 预测样本总数                |
| 字段检查                 | O(c)                   | c 为必要字段数量                            |
| 概率清洗与裁剪           | O(n)                   | 将概率转数值并裁剪到安全范围                |
| Platt Scaling 拟合       | 约 O(t * n_valid)      | t 为逻辑回归迭代次数，输入是一维 logit 概率 |
| Isotonic Regression 拟合 | O(n_valid log n_valid) | 同分布回归通常需要排序                      |
| 生成校准概率             | O(n)                   | 对 valid/test 生成 Platt 和 Isotonic 概率   |
| AUC / PR-AUC             | O(n log n)             | 排序类指标需要按概率排序                    |
| Brier Score / Log Loss   | O(n)                   | 逐样本计算概率误差                          |
| ECE / MCE 分箱           | O(n * b)               | b 为分箱数量，本配置为 10                   |
| Top 比例评估             | O(n log k)             | 使用 nlargest 获取 TopK 样本                |

设预测样本总数为 `n`，验证集样本数为 `n_valid`，分箱数量为 `b`，TopK 样本数量为 `k`。本工程不重新训练 LightGBM，只对已有概率做校准，因此整体计算成本明显低于模型训练阶段。

Platt Scaling 输入是一维 logit 概率，因此训练成本较低。Isotonic Regression 通常需要排序，复杂度约为：

```text
O(n_valid log n_valid)
```

AUC 和 PR-AUC 也是排序类指标，复杂度为：

```text
O(n log n)
```

Top 比例评估使用 `nlargest` 获取概率最高的 TopK 样本，复杂度为：

```text
O(n log k)
```

整体来看，概率校准模块的性能压力较小，主要适合作为 LightGBM 模型训练后的后处理步骤。

## 17. 本地运行验证步骤

在本地项目目录中准备好 LightGBM 最优模型预测文件：

```text
lgbm_predictions_best_with_path.csv
```

确认配置文件中的路径正确后，运行：

```bash
python run_lgbm_calibration.py
```

运行成功后，应看到类似输出：

```text
LightGBM 概率校准完成！

输出文件位置：
calibrated_prediction_path: ...
metrics_path: ...
bin_path: ...
top_path: ...
calibrator_path: ...
```

随后检查输出目录中是否生成以下文件：

```text
calibrated_lgbm_predictions_with_path.csv
lgbm_calibration_metrics_with_path.csv
lgbm_calibration_bin_report_with_path.csv
lgbm_calibration_top_rate_metrics_with_path.csv
lgbm_probability_calibrators_with_path.joblib
```

如果以上文件均正常生成，且 metrics 文件中 original、platt、isotonic 三种方法在 valid/test 上均有指标，则说明概率校准模块运行测试通过。

## 18. 改进建议

首先，建议增加输入文件存在性检查。如果 `lgbm_predictions_best_with_path.csv` 不存在，应直接提示用户检查路径，而不是只显示底层 CSV 读取错误。

其次，建议在输出指标中增加“相对原始概率的变化量”，例如 Platt 和 Isotonic 相比 original 的 Brier Score 下降幅度、Log Loss 下降幅度和 ECE 下降幅度，这样更容易判断校准是否有效。

再次，建议在校准报告中增加“推荐使用概率字段”的自动判断逻辑。例如，如果 Platt 在 test 集 ECE 和 Brier Score 上均优于 original，则建议概率解释场景使用 Platt 概率。

最后，建议将分箱校准报告可视化为可靠性曲线，使模型概率是否偏高或偏低更加直观。

## 19. 测试结论

综合本次测试结果，LightGBM 概率校准工程的代码结构基本完整。配置文件能够指定输入预测结果、输出目录、目标字段、概率字段、分箱数量、Top 评估比例和输出文件名；核心代码能够完成字段检查、概率裁剪、valid/test 划分、Platt Scaling 校准、Isotonic Regression 校准、校准概率输出、整体指标计算、分箱校准报告、Top 比例评估和校准器保存；运行入口脚本能够调用统一接口完成完整流程。

从静态检查角度看，本模块测试结论为：配置文件测试通过，核心函数封装测试通过，Platt Scaling 测试通过，Isotonic Regression 测试通过，校准指标测试通过，分箱校准报告测试通过，Top 比例评估测试通过，输出文件设计测试通过。由于当前没有上传真实预测结果文件和运行输出结果，输入文件读取测试和实际校准效果测试需要在本地运行后进一步确认。
