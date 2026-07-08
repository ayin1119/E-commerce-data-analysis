from config_lgbm_calibration import LGBM_CALIBRATION_CONFIG
from lgbm_calibration import run_lgbm_calibration


outputs = run_lgbm_calibration(LGBM_CALIBRATION_CONFIG)

print("LightGBM 概率校准完成！")
print("\n输出文件位置：")
for name, path in outputs.items():
    print(name, ":", path)
