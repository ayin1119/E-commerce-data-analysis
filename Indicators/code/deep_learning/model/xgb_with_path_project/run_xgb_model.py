from config_xgb import XGB_CONFIG
from xgboost_purchase_pipeline import run_xgb_experiment


outputs = run_xgb_experiment(XGB_CONFIG)

print("XGBoost 购买概率模型实验完成！")
print("最优实验：", outputs["best_experiment"])
print("\n输出文件位置：")
for name, path in outputs.items():
    if name.endswith("_path"):
        print(name, ":", path)
