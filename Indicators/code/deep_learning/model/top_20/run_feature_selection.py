from config_feature_selection import FEATURE_SELECTION_CONFIG
from feature_selection_experiment import run_feature_selection_experiment


outputs = run_feature_selection_experiment(FEATURE_SELECTION_CONFIG)

print("特征筛选实验完成！")
print("最优实验：", outputs["best_experiment"])
print("\n输出文件位置：")
for name, path in outputs.items():
    if name.endswith("_path"):
        print(name, ":", path)
