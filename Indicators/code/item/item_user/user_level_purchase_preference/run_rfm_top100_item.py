from config import RFM_TOP100_ITEM_CONFIG
from rfm_top100_item_pipeline import run_rfm_top100_item_analysis


result, output_path = run_rfm_top100_item_analysis(
    RFM_TOP100_ITEM_CONFIG
)

print("RFM 各层级 Top100 商品购买偏好分析完成！")
print("结果保存位置：", output_path)

print("结果预览：")
print(result.head(20))