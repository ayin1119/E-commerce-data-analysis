from config import RFM_CONFIG
from rfm_pipeline import run_rfm_analysis

rfm_result, rfm_summary, saved_paths = run_rfm_analysis(RFM_CONFIG)

print("RFM 分析完成！")
print("用户级结果保存位置：", saved_paths[0])
print("汇总结果保存位置：", saved_paths[1])
