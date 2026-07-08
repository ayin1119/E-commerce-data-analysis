# 电商用户-商品 7 天购买概率预测交互式仪表盘

这个项目包是基于你上传的 XGBoost 校准结果文件制作的 Streamlit 可交互式仪表盘。

## 一、怎么运行

进入本文件夹后，在终端运行：

```bash
pip install -r requirements.txt
streamlit run app.py
```

Mac 用户也可以双击：

```text
run_dashboard_mac.command
```

如果系统提示没有权限，可以在终端运行：

```bash
chmod +x run_dashboard_mac.command
./run_dashboard_mac.command
```

## 二、仪表盘包含什么

仪表盘共 6 个页面：

1. 项目总览  
   展示样本量、真实购买率、AUC、PR-AUC、ECE、Top-K 购买率和召回率，以及报告中的模型对比结果。

2. Top-K 业务筛选  
   通过滑动条选择 Top 1% 到 Top 30% 的高购买概率候选池，实时查看概率阈值、候选样本数、购买率、召回率和候选用户商品明细。

3. 概率校准分析  
   对比 Original、Platt、Isotonic 三种概率版本的 Brier Score、Log Loss、ECE、平均预测概率和真实购买率，并展示 Reliability Curve。

4. 错误样本分析  
   在 Top-K 口径下展示 TP、FP、FN、TN，并提供高分未购买样本、低分实际购买样本的表格和导出功能。

5. 预测明细查询  
   支持按真实标签、预测概率范围、商品类别筛选用户-商品预测结果，并导出 CSV。

6. 使用说明  
   说明运行方式、页面含义和数据文件用途。

## 三、数据来源

`data/` 文件夹中包含：

| 文件 | 说明 |
|---|---|
| predictions.csv | 用户-商品预测概率、真实标签、原始概率、Platt 校准概率、Isotonic 校准概率 |
| calibration_metrics.csv | XGBoost 概率校准整体指标 |
| calibration_bin_report.csv | XGBoost 概率校准分箱结果 |
| top_rate_metrics.csv | Top5%、Top10%、Top20% 购买率和召回率 |
| model_comparison_from_report.csv | 根据项目总结报告整理的模型效果对比表 |
| feature_explanation_from_report.csv | 根据项目总结报告整理的特征业务解释表 |
| final_purchase_model_evaluation_report_updated.md | 项目总结报告原文 |
| xgb_probability_calibrators.joblib | XGBoost 概率校准器文件，当前仪表盘主要用于结果展示，没有调用它重新预测 |

## 四、推荐展示口径

如果用于答辩或项目展示，建议这样讲：

> 本项目补充了一个基于 Streamlit 的交互式仪表盘。仪表盘不是重新训练模型，而是把已经训练好的 XGBoost 购买概率预测结果转化为业务筛选工具。用户可以选择概率校准方法、数据集和 Top 候选池比例，实时查看候选池购买率、召回率、概率阈值、错误样本和候选用户商品明细。相比静态报告，仪表盘更直观地展示了模型在推荐排序和营销触达场景中的应用价值。

## 五、注意事项

当前仪表盘基于预测结果表进行展示和分析，没有做实时单条预测。原因是你这次上传的是校准后的预测结果和校准器文件，不是完整的原始特征宽表。如果后续要做“输入用户商品特征，实时预测购买概率”，需要再补充最终模型文件和对应的 62 个入模特征字段。
