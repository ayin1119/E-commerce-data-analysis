from config_xgb_calibration import XGB_CALIBRATION_CONFIG
from xgb_calibration import run_xgb_calibration


outputs = run_xgb_calibration(XGB_CALIBRATION_CONFIG)

print("XGBoost 概率校准完成！")
print("\n输出文件位置：")
for name, path in outputs.items():
    print(name, ":", path)
