from config_lgbm import LGBM_CONFIG
from lightgbm_purchase_pipeline import run_lgbm_experiment


outputs = run_lgbm_experiment(LGBM_CONFIG)

print("LightGBM 购买概率模型实验完成！")
print("最优实验：", outputs["best_experiment"])
print("\n输出文件位置：")
for name, path in outputs.items():
    if name.endswith("_path"):
        print(name, ":", path)
