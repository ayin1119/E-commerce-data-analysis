from config import USER_CHURN_CONFIG
from user_churn_pipeline import run_user_churn_analysis


result, output_path = run_user_churn_analysis(
    USER_CHURN_CONFIG
)

print("流失用户分析完成！")
print("结果保存位置：", output_path)

print("结果预览：")
print(result.head(20))

print("各类用户数量：")
print(result["churn_label"].value_counts())