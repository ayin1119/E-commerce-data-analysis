# E-commerce Data Analysis

本项目是一个基于电商用户行为数据的综合分析与购买概率预测工程。工程前半部分围绕用户、商品、时间和行为路径四个维度进行指标分析，后半部分在指标分析的基础上构建机器学习特征宽表，并使用逻辑回归、LightGBM、XGBoost 等模型预测“用户-商品组合在未来 7 天是否会发生购买”。最终项目补充了模型评估报告和 Streamlit 交互式仪表盘，用于展示模型效果、概率校准结果、Top-K 高购买概率候选池和错误样本分析。

当前仓库的主目录结构以 `Indicators/` 为核心，下面分为 `code/`、`form/`、`report/` 三类内容：`code/` 存放 SQL 与建模代码，`form/` 存放中间表和输出结果，`report/` 存放分析报告、模型评估报告和仪表盘工程。

---

## 1. 项目目标

本项目主要完成两类任务。

第一类是电商行为指标分析。基于用户行为日志，分析用户活跃度、商品表现、品类表现、行为路径、留存复购、购买价值等指标，形成时间维度、用户维度、商品维度和路径维度的多角度分析结果。

第二类是购买概率预测。项目将用户历史行为、商品热度、用户-商品交叉行为、用户-品类偏好和行为路径特征整合为特征宽表，构建二分类模型，预测某个用户未来 7 天是否会购买某个商品。该预测结果可以用于推荐排序、营销触达候选池筛选和用户-商品购买概率预估。

---

## 2. 技术栈

项目主要使用以下工具和技术：

| 类型         | 工具                                    |
| ------------ | --------------------------------------- |
| 数据库       | MySQL                                   |
| 数据处理     | SQL、Python、pandas、numpy              |
| 建模评估     | scikit-learn、LightGBM、XGBoost、joblib |
| 可视化       | matplotlib、seaborn、plotly             |
| 交互式仪表盘 | Streamlit                               |
| 项目管理     | Git、GitHub                             |

说明：根目录的 `requirements.txt` 是从本地环境导出的较完整依赖文件，可能包含本机路径形式的依赖。如果在其他电脑上安装失败，建议优先使用各模块自己的 `requirements.txt`，例如仪表盘目录下的 `Indicators/report/deep_learning/purchase_probability_dashboard/requirements.txt`。

---

## 3. 数据字段说明

原始行为表主要围绕以下字段展开：

| 字段              | 含义                                                          |
| ----------------- | ------------------------------------------------------------- |
| `user_id`       | 用户 ID                                                       |
| `item_id`       | 商品 ID                                                       |
| `item_category` | 商品类别 ID                                                   |
| `behavior_type` | 行为类型，通常 1 表示浏览，2 表示收藏，3 表示加购，4 表示购买 |
| `event_time`    | 行为发生时间                                                  |

在购买概率预测任务中，最终标签字段为：

| 字段             | 含义                                                |
| ---------------- | --------------------------------------------------- |
| `label_buy_7d` | 是否在未来 7 天购买该商品，1 表示购买，0 表示未购买 |

模型输出概率字段包括：

| 字段                     | 含义                             |
| ------------------------ | -------------------------------- |
| `buy_probability`      | 逻辑回归模型输出概率             |
| `lgbm_probability`     | LightGBM 模型输出概率            |
| `xgb_probability`      | XGBoost 模型输出概率             |
| `platt_probability`    | Platt Scaling 校准后的概率       |
| `isotonic_probability` | Isotonic Regression 校准后的概率 |

---

## 4. 工程目录结构

当前仓库的核心结构如下：

```text
E-commerce-data-analysis/
├── README.md
├── requirements.txt
└── Indicators/
    ├── code/
    │   ├── Behavioral_path/
    │   │   ├── Mode_statistics/
    │   │   └── path_user/
    │   ├── item/
    │   │   ├── category_performance/
    │   │   ├── item_behavior/
    │   │   ├── item_performance/
    │   │   └── item_user/
    │   ├── time/
    │   │   ├── Derived_feature/
    │   │   ├── daily_trend/
    │   │   ├── hour_trend/
    │   │   └── week_trend/
    │   ├── user/
    │   │   ├── Activity_level/
    │   │   ├── Behavioral_preferences/
    │   │   ├── Cross_features/
    │   │   ├── Retention_Repeat_Purchase/
    │   │   └── purchase_value/
    │   └── deep_learning/
    │       ├── indicators/
    │       └── model/
    ├── form/
    │   ├── Behavioral_path/
    │   ├── deep_learning/
    │   ├── item/
    │   ├── time/
    │   └── user/
    └── report/
        ├── Behavioral_path/
        ├── deep_learning/
        ├── item/
        ├── time/
        └── user/
```

其中 `Indicators/report/deep_learning/purchase_probability_dashboard/` 是当前可交互式仪表盘工程，包含 `app.py`、`data/`、`requirements.txt` 和 `run_dashboard_mac.command`。

---

## 5. 模块划分与功能说明

### 5.1 时间维度分析模块

路径：

```text
Indicators/code/time/
Indicators/form/time/
Indicators/report/time/
```

该模块主要分析用户行为随时间变化的规律，包括日活跃、小时活跃、周活跃和衍生时间特征。对应代码目录包括：

| 子目录               | 功能                         |
| -------------------- | ---------------------------- |
| `Derived_feature/` | 构建时间相关衍生字段         |
| `daily_trend/`     | 分析每日行为趋势和日活跃变化 |
| `hour_trend/`      | 分析不同小时段的用户行为高峰 |
| `week_trend/`      | 分析周维度活跃变化           |

---

### 5.2 用户维度分析模块

路径：

```text
Indicators/code/user/
Indicators/form/user/
Indicators/report/user/
```

该模块围绕用户行为强度、用户偏好、交叉特征、留存复购和购买价值展开分析。

| 子目录                         | 功能                                     |
| ------------------------------ | ---------------------------------------- |
| `Activity_level/`            | 用户活跃度分析                           |
| `Behavioral_preferences/`    | 用户行为偏好和常访问品类分析             |
| `Cross_features/`            | 用户与商品、品类之间的交叉特征分析       |
| `Retention_Repeat_Purchase/` | 留存率、复购率、购买频率分析             |
| `purchase_value/`            | 用户购买价值、购买率、购买次数等指标分析 |

---

### 5.3 商品与品类分析模块

路径：

```text
Indicators/code/item/
Indicators/form/item/
Indicators/report/item/
```

该模块主要分析商品和品类的浏览、收藏、加购、购买情况，以及商品转化率和品类表现。

| 子目录                    | 功能                                     |
| ------------------------- | ---------------------------------------- |
| `category_performance/` | 品类表现分析，包括品类行为量和转化情况   |
| `item_behavior/`        | 商品行为统计，包括浏览、收藏、加购、购买 |
| `item_performance/`     | 商品销量、转化率和综合表现分析           |
| `item_user/`            | 商品与用户交互关系分析                   |

---

### 5.4 行为路径分析模块

路径：

```text
Indicators/code/Behavioral_path/
Indicators/form/Behavioral_path/
Indicators/report/Behavioral_path/
```

该模块用于分析用户从浏览到购买之间的行为路径，例如浏览-购买、浏览-加购-购买、浏览-收藏-加购-购买等路径，并统计不同路径类型的数量和转化情况。

| 子目录               | 功能               |
| -------------------- | ------------------ |
| `Mode_statistics/` | 行为路径模式统计   |
| `path_user/`       | 用户级行为路径分析 |

行为路径分析结果后续也被用于机器学习特征工程，例如 `pre_buy_behavior_count`、`purchase_count` 和 `pre_buy_behavior_per_purchase` 等行为路径特征。

---

### 5.5 机器学习特征工程模块

路径：

```text
Indicators/code/deep_learning/indicators/
```

该目录存放购买概率预测所需的 SQL 特征构建脚本。主要文件包括：

| 文件                                   | 功能                            |
| -------------------------------------- | ------------------------------- |
| `ml_window_config.sql`               | 设置样本窗口和标签窗口          |
| `ml_candidate_user_item_all.sql`     | 构建候选用户-商品组合           |
| `ml_future_purchase_pair_all.sql`    | 构建未来购买标签所需的购买对    |
| `ml_label_buy_7d_sampled.sql`        | 构建未来 7 天购买标签并进行采样 |
| `ml_user_feature_7d_all.sql`         | 构建用户 7 天行为特征           |
| `ml_item_feature_7d_all.sql`         | 构建商品 7 天行为特征           |
| `ml_user_item_feature_7d_all.sql`    | 构建用户-商品交叉行为特征       |
| `ml_sampled_user_categories_all.sql` | 构建用户-品类相关特征           |
| `ml_feature_wide_table_v1.sql`       | 汇总生成模型训练所需特征宽表    |

特征宽表主要包含用户整体特征、商品整体特征、用户-商品交叉特征、用户-品类交叉特征和行为路径特征。

---

### 5.6 机器学习建模模块

路径：

```text
Indicators/code/deep_learning/model/
```

该目录存放不同版本模型训练、预测、评估和校准代码。

| 子目录                                            | 功能                                   |
| ------------------------------------------------- | -------------------------------------- |
| `purchase_probability_model_project/`           | 基础购买概率预测模型项目               |
| `top_20/`                                       | Top20 特征筛选实验                     |
| `lgbm_with_path_project/`                       | 加入行为路径特征后的 LightGBM 模型实验 |
| `xgb_with_path_project/`                        | 加入行为路径特征后的 XGBoost 模型实验  |
| `lgbm_calibration_project/`                     | LightGBM 概率校准实验                  |
| `xgb_calibration/`                              | XGBoost 概率校准实验                   |
| `purchase_probability_model_with_path_project/` | 加入路径特征后的购买概率预测工程版本   |

---

### 5.7 结果输出模块

路径：

```text
Indicators/form/
```

`form/` 目录用于保存 SQL 和 Python 输出的结果表。其结构和 `code/` 保持一致，方便根据模块找到对应结果。

深度学习结果主要位于：

```text
Indicators/form/deep_learning/
```

该目录下包含：

| 子目录                                    | 内容                       |
| ----------------------------------------- | -------------------------- |
| `raw/`                                  | 原始比例或初始模型相关输出 |
| `1_50/`、`1_20/`、`1_10/`、`1_5/` | 不同正负样本比例版本输出   |
| `top_20/`                               | Top20 特征版本输出         |
| `lightgbm/`                             | LightGBM 模型输出          |
| `with_path/`                            | 行为路径特征版本输出       |
| `lgbm_calibration_outputs/`             | LightGBM 概率校准结果      |
| `xgb_with_path_outputs/`                | XGBoost 路径特征模型输出   |
| `xgb_calibration_outputs/`              | XGBoost 概率校准结果       |

---

### 5.8 报告与仪表盘模块

路径：

```text
Indicators/report/
```

该目录保存项目报告和可视化展示内容。深度学习模型报告主要位于：

```text
Indicators/report/deep_learning/
```

其中包括：

| 子目录或文件                                          | 功能                         |
| ----------------------------------------------------- | ---------------------------- |
| `lr/`                                               | 逻辑回归模型报告             |
| `feature_selection/`                                | 特征筛选报告                 |
| `lgbm/`                                             | LightGBM 模型报告            |
| `xgb/`                                              | XGBoost 模型报告             |
| `lgbm_calibration/`                                 | LightGBM 概率校准报告        |
| `xgb_calibration/`                                  | XGBoost 概率校准报告         |
| `with_path/`                                        | 加入行为路径特征后的模型报告 |
| `purchase_probability_dashboard/`                   | Streamlit 交互式仪表盘工程   |
| `final_purchase_model_evaluation_report_updated.md` | 最终模型评估总报告           |

---

## 6. 模型实验总结

本项目先后完成了以下模型实验：

1. 原始 65 字段逻辑回归模型。
2. 不同正负样本比例版本实验，包括原始比例、1:50、1:20、1:10 和 1:5。
3. 加入行为路径特征后的 68 字段模型。
4. Top20、Top30、Top40、Top50 和全特征版本对比。
5. LightGBM 非线性模型实验。
6. XGBoost 非线性模型实验。
7. LightGBM 和 XGBoost 概率校准实验。
8. Top-K 高购买概率候选池评估和错误样本分析。

最终模型评估报告显示，树模型整体明显优于逻辑回归模型。XGBoost 全特征版本在测试集 PR-AUC 和 Top10% 指标上表现较好，适合推荐排序和高购买概率用户-商品筛选；概率校准版本更适合用于业务概率解释。

---

## 7. 可交互式仪表盘

仪表盘路径：

```text
Indicators/report/deep_learning/purchase_probability_dashboard/
```

仪表盘基于 Streamlit 构建，主要用于展示已经训练好的 XGBoost 概率预测和校准结果，不重新训练模型。

### 7.1 仪表盘页面

仪表盘包含 6 个页面：

| 页面           | 功能                                                           |
| -------------- | -------------------------------------------------------------- |
| 项目总览       | 展示样本量、真实购买率、AUC、PR-AUC、ECE、Top-K 购买率和召回率 |
| Top-K 业务筛选 | 通过滑动条选择 Top 1% 到 Top 30% 的高购买概率候选池            |
| 概率校准分析   | 对比 Original、Platt、Isotonic 三种概率版本的校准效果          |
| 错误样本分析   | 展示 TP、FP、FN、TN，并输出高分未购买和低分实际购买样本        |
| 预测明细查询   | 支持按标签、概率范围、商品类别筛选预测结果                     |
| 使用说明       | 说明页面含义、运行方式和数据文件用途                           |

### 7.2 仪表盘运行方式

进入仪表盘目录：

```bash
cd Indicators/report/deep_learning/purchase_probability_dashboard
```

创建并激活虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

运行仪表盘：

```bash
streamlit run app.py
```

Mac 用户也可以运行：

```bash
chmod +x run_dashboard_mac.command
./run_dashboard_mac.command
```

浏览器打开后，默认地址通常是：

```text
http://localhost:8501
```

---

## 8. 推荐复现流程

如果需要从头复现整个工程，建议按下面顺序执行。

### Step 1：准备数据库

将原始电商用户行为数据导入 MySQL。建议统一使用一张主表，例如：

```text
data_min
```

字段至少应包含：

```text
user_id, item_id, item_category, behavior_type, event_time
```

### Step 2：完成基础指标分析

按分析主题运行 `Indicators/code/` 下的 SQL 或 Python 脚本：

```text
Indicators/code/time/
Indicators/code/user/
Indicators/code/item/
Indicators/code/Behavioral_path/
```

运行后将结果输出到对应的 `Indicators/form/` 子目录，并在 `Indicators/report/` 中形成分析报告。

### Step 3：构建机器学习特征

依次运行：

```text
Indicators/code/deep_learning/indicators/ml_window_config.sql
Indicators/code/deep_learning/indicators/ml_candidate_user_item_all.sql
Indicators/code/deep_learning/indicators/ml_future_purchase_pair_all.sql
Indicators/code/deep_learning/indicators/ml_label_buy_7d_sampled.sql
Indicators/code/deep_learning/indicators/ml_user_feature_7d_all.sql
Indicators/code/deep_learning/indicators/ml_item_feature_7d_all.sql
Indicators/code/deep_learning/indicators/ml_user_item_feature_7d_all.sql
Indicators/code/deep_learning/indicators/ml_sampled_user_categories_all.sql
Indicators/code/deep_learning/indicators/ml_feature_wide_table_v1.sql
```

该步骤会生成用于模型训练的用户-商品特征宽表。

### Step 4：训练和评估模型

运行 `Indicators/code/deep_learning/model/` 下的模型代码，完成逻辑回归、特征筛选、LightGBM、XGBoost 和概率校准实验。

模型输出建议保存到：

```text
Indicators/form/deep_learning/
```

模型报告建议保存到：

```text
Indicators/report/deep_learning/
```

### Step 5：运行仪表盘

进入：

```text
Indicators/report/deep_learning/purchase_probability_dashboard/
```

执行：

```bash
streamlit run app.py
```

---

## 9. 关键评估指标

由于购买预测是正样本相对稀少的二分类任务，因此项目不以准确率作为核心指标，而主要关注：

| 指标                           | 作用                                     |
| ------------------------------ | ---------------------------------------- |
| AUC                            | 衡量模型整体排序能力                     |
| PR-AUC                         | 更关注正样本识别能力，适合不平衡分类任务 |
| Top5% / Top10% / Top20% 购买率 | 衡量高分候选池中真实购买比例             |
| Top-K Recall                   | 衡量高分候选池能覆盖多少真实购买样本     |
| Brier Score                    | 衡量概率预测误差                         |
| Log Loss                       | 衡量概率预测质量                         |
| ECE                            | 衡量概率校准误差                         |
| 训练耗时、模型大小、预测速度   | 衡量工程部署可行性                       |

---

## 10. 当前工程边界

当前工程已经覆盖从电商行为指标分析到购买概率模型评估和仪表盘展示的完整流程，但仍有一些边界需要注意：

1. 原始数据未直接纳入仓库，需要用户在本地 MySQL 中准备。
2. 根目录 `requirements.txt` 可能包含本地环境路径，跨设备复现时可能需要重新整理依赖。
3. 仪表盘当前基于预测结果表展示，不执行实时单条预测。
4. 若要在仪表盘中输入用户商品特征并实时预测，需要补充最终模型文件和完整入模特征 schema。
5. 仓库中如果存在 `.DS_Store`、`.venv/` 等本地临时文件，建议后续从 Git 中移除，并加入 `.gitignore`。

---

## 11. 后续改进方向

后续可以继续完善以下内容：

1. 在原始真实比例数据上训练 LightGBM / XGBoost，进一步贴近线上业务分布。
2. 增加滚动时间窗口验证，检验模型在不同时间段的稳定性。
3. 在错误分析中加入品类、用户活跃度、行为路径类型的分层分析。
4. 整理一份轻量级 `requirements_min.txt`，避免完整 conda 环境导出导致安装失败。
5. 将仪表盘中的预测结果展示升级为实时预测功能。
6. 增加模型训练流程图、数据流向图和最终特征字典。

---

## 12. 仓库维护建议

建议保持以下提交规范：

```bash
git add README.md
git commit -m "Update project README"
git push origin master
```

如果需要清理 macOS 临时文件：

```bash
find . -name ".DS_Store" -delete
git rm --cached -r --ignore-unmatch .DS_Store
```

如果需要避免提交虚拟环境：

```gitignore
.venv/
__pycache__/
*.pyc
.DS_Store
```

---

## 13. 项目一句话总结

本项目从电商用户行为数据出发，完成了时间、用户、商品和行为路径多维指标分析，并进一步构建用户-商品购买概率预测模型，最终通过模型评估报告和 Streamlit 仪表盘展示模型在推荐排序、营销触达和购买概率解释中的业务价值。
