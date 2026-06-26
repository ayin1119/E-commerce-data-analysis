from config import OVERALL_CORE_PURCHASE_CONFIG
from overall_core_purchase_pipeline import run_overall_core_purchase_analysis


result, output_path = run_overall_core_purchase_analysis(
    OVERALL_CORE_PURCHASE_CONFIG
)

print("整体核心用户购买率分析完成！")
print("结果保存位置：", output_path)

print("结果预览：")
print(result)