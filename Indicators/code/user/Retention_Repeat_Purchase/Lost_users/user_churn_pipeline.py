from pathlib import Path
import pandas as pd
import numpy as np


def load_user_purchase_interval(config):
    """
    接口定义：
    输入：
        config：配置参数字典

    输出：
        df：用户最近一次购买间隔表

    作用：
        读取最近一次购买时间表，只保留后续分析需要的字段。
    """
    user_col = config["user_col"]
    days_col = config["days_col"]
    hours_col = config["hours_col"]

    df = pd.read_csv(
        config["input_path"],
        usecols=[user_col, days_col, hours_col]
    )

    return df


def check_required_columns(df, config):
    """
    接口定义：
    输入：
        df：用户最近一次购买间隔表
        config：配置参数字典

    输出：
        无

    作用：
        检查必要字段是否存在。
        如果缺少字段，就给出容易看懂的报错。
    """
    required_columns = [
        config["user_col"],
        config["days_col"],
        config["hours_col"]
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "缺少必要字段："
            + "、".join(missing_columns)
            + "。请检查输入 CSV 文件的列名是否正确。"
        )


def clean_user_purchase_interval(df, config):
    """
    接口定义：
    输入：
        df：原始用户最近一次购买间隔表
        config：配置参数字典

    输出：
        cleaned_df：清洗后的用户表

    作用：
        将天数和小时数字段转成数值类型。
        去掉 days_since_last_purchase 为空的用户。
    """
    user_col = config["user_col"]
    days_col = config["days_col"]
    hours_col = config["hours_col"]

    cleaned_df = df.copy()

    cleaned_df[days_col] = pd.to_numeric(
        cleaned_df[days_col],
        errors="coerce"
    )

    cleaned_df[hours_col] = pd.to_numeric(
        cleaned_df[hours_col],
        errors="coerce"
    )

    cleaned_df = cleaned_df.dropna(
        subset=[user_col, days_col]
    )

    # 如果 hours_since_last_purchase 为空，用 0 补充
    cleaned_df[hours_col] = cleaned_df[hours_col].fillna(0)

    return cleaned_df


def calculate_churn_thresholds(cleaned_df, config):
    """
    接口定义：
    输入：
        cleaned_df：清洗后的用户表
        config：配置参数字典

    输出：
        churn_threshold：流失用户阈值
        risk_threshold：流失倾向用户阈值

    作用：
        使用分位数计算分层阈值。
        不再对所有用户做完整排序，从而降低时间复杂度。

    说明：
        距离上次购买时间越长，越容易流失。
        前 20% 距离最长的用户，对应 80% 分位数以上。
        前 50% 距离最长的用户，对应 50% 分位数以上。
    """
    days_col = config["days_col"]
    churn_ratio = config["churn_ratio"]
    risk_ratio = config["risk_ratio"]

    churn_quantile = 1 - churn_ratio
    risk_quantile = 1 - risk_ratio

    churn_threshold = cleaned_df[days_col].quantile(churn_quantile)
    risk_threshold = cleaned_df[days_col].quantile(risk_quantile)

    return churn_threshold, risk_threshold


def add_churn_labels_by_threshold(cleaned_df, churn_threshold, risk_threshold, config):
    """
    接口定义：
    输入：
        cleaned_df：清洗后的用户表
        churn_threshold：流失用户阈值
        risk_threshold：流失倾向用户阈值
        config：配置参数字典

    输出：
        result：增加流失标签后的用户表

    作用：
        根据分位数阈值给用户打标签。
        不做完整排序，时间复杂度接近 O(n)。
    """
    days_col = config["days_col"]

    result = cleaned_df.copy()

    result["churn_threshold"] = churn_threshold
    result["risk_threshold"] = risk_threshold

    result["churn_label"] = np.select(
        [
            result[days_col] >= churn_threshold,
            result[days_col] >= risk_threshold
        ],
        [
            "流失用户",
            "有流失倾向用户"
        ],
        default="普通用户"
    )

    return result


def add_rank_if_needed(result, config):
    """
    接口定义：
    输入：
        result：已经有流失标签的结果表
        config：配置参数字典

    输出：
        result：根据配置决定是否增加排名字段

    作用：
        如果 keep_rank = True，就按最近购买间隔完整排序，并生成排名。
        如果 keep_rank = False，就不排序，以保留时间复杂度优化效果。
    """
    if not config["keep_rank"]:
        return result

    user_col = config["user_col"]
    days_col = config["days_col"]
    hours_col = config["hours_col"]

    result = result.sort_values(
        by=[days_col, hours_col, user_col],
        ascending=[False, False, True]
    ).reset_index(drop=True)

    result["user_rank"] = result.index + 1

    result["rank_rate"] = (
        result["user_rank"] / len(result)
    ).round(4)

    return result


def save_result(result, config):
    """
    接口定义：
    输入：
        result：最终流失用户结果表
        config：配置参数字典

    输出：
        output_path：结果保存路径

    作用：
        将结果保存成 CSV 文件。
    """
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / config["output_filename"]

    result.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    return output_path


def run_user_churn_analysis(config):
    """
    统一接口定义：
    输入：
        config：配置参数字典

    输出：
        result：流失用户分层结果表
        output_path：结果保存路径

    作用：
        外部只需要调用这个函数，就可以完成完整分析流程。
    """
    df = load_user_purchase_interval(config)

    check_required_columns(
        df,
        config
    )

    cleaned_df = clean_user_purchase_interval(
        df,
        config
    )

    churn_threshold, risk_threshold = calculate_churn_thresholds(
        cleaned_df,
        config
    )

    result = add_churn_labels_by_threshold(
        cleaned_df,
        churn_threshold,
        risk_threshold,
        config
    )

    result = add_rank_if_needed(
        result,
        config
    )

    output_path = save_result(
        result,
        config
    )

    return result, output_path