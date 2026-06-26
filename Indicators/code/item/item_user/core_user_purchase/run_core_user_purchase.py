from config import CORE_USER_PURCHASE_CONFIG
from core_user_purchase_pipeline import run_core_user_purchase_analysis


item_core_purchase, output_path = run_core_user_purchase_analysis(
    CORE_USER_PURCHASE_CONFIG
)

print("商品核心用户购买率分析完成！")
print("结果保存位置：", output_path)

print("结果预览：")
print(item_core_purchase.head(20))