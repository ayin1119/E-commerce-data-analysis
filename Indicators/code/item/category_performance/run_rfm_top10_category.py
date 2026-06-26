from config import TOP10_CATEGORY_CONFIG
from rfm_top10_category_pipeline import run_rfm_top10_category_analysis


result, output_path = run_rfm_top10_category_analysis(TOP10_CATEGORY_CONFIG)

print("RFM 各层级 Top10 商品类别分析完成！")
print("结果保存位置：", output_path)

print("结果预览：")
print(result.head(20))