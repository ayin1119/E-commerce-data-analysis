from config import PURCHASE_MODEL_CONFIG
from purchase_probability_pipeline import run_purchase_probability_model


outputs = run_purchase_probability_model(PURCHASE_MODEL_CONFIG)

print("购买概率模型训练完成！")
print("特征数量：", outputs["feature_count"])
print("训练集形状：", outputs["train_shape"])
print("验证集形状：", outputs["valid_shape"])
print("测试集形状：", outputs["test_shape"])

print("\n输出文件位置：")
for name, path in outputs.items():
    if name.endswith("_path"):
        print(name, ":", path)
