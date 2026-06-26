from pathlib import Path
import pandas as pd
import numpy as np


def load_data(config):
    """
    接口定义：
    输入：config 配置字典
    输出：三张 DataFrame 表
    作用：读取最近一次购买时间、购买频率、购买数购买率三张表
    """
    last_purchase = pd.read_csv(config["last_purchase_path"])
    purchase_freq = pd.read_csv(config["purchase_freq_path"])
    purchase_value = pd.read_csv(config["purchase_value_path"])

    return last_purchase, purchase_freq, purchase_value


def merge_tables(last_purchase, purchase_freq, purchase_value, merge_key="user_id"):
    """
    接口定义：
    输入：三张 DataFrame 表，共同字段 merge_key
    输出：合并后的 DataFrame
    作用：把三张用户表按 user_id 横向合并
    """
    df = last_purchase.merge(
        purchase_freq,
        on=merge_key,
        how="outer"
    )

    df = df.merge(
        purchase_value,
        on=merge_key,
        how="outer"
    )

    return df


def convert_numeric_columns(df, numeric_columns):
    """
    接口定义：
    输入：合并后的 DataFrame，需要转数字的列名列表
    输出：转换后的 DataFrame
    作用：把 RFM 计算需要用到的字段转成数字，避免字符串导致计算报错
    """
    df = df.copy()

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def check_required_columns(df, required_columns):
    """
    接口定义：
    输入：DataFrame，必须存在的列名列表
    输出：没有返回值
    作用：检查关键字段是否存在，不存在就给出容易看懂的报错
    """
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            "缺少必要字段："
            + "、".join(missing_columns)
            + "。请检查三个 csv 文件的列名是否正确。"
        )


def split_purchase_users(df):
    """
    接口定义：
    输入：合并后的 DataFrame
    输出：有购买用户表、未购买用户表
    作用：RFM 只适合给已经购买过的用户打分，未购买用户单独归为“未购买用户”
    """
    purchase_users = df[df["purchase_count"].fillna(0) > 0].copy()
    non_purchase_users = df[df["purchase_count"].fillna(0) <= 0].copy()

    return purchase_users, non_purchase_users


def make_score_by_quantile(series, score_bins, high_score_first):
    """
    接口定义：
    输入：
        series：要打分的字段
        score_bins：分成几档，通常是 5
        high_score_first：True 表示数值越小分越高；False 表示数值越大分越高
    输出：分数列
    作用：按照分位数给用户打 1~5 分

    举例：
        R_score：days_since_last_purchase 越小越好，所以 high_score_first=True
        F_score：purchase_day_frequency 越大越好，所以 high_score_first=False
        M_score：purchase_count 越大越好，所以 high_score_first=False
    """
    result = pd.Series(np.nan, index=series.index)

    valid_series = series.dropna()

    if valid_series.empty:
        return result

    # 如果数据量少于 5 个用户，就不能强行分成 5 档，所以取较小值
    real_bins = min(score_bins, len(valid_series))

    if real_bins <= 1:
        result.loc[valid_series.index] = 5 if high_score_first else 1
        return result.astype(float)

    ranked_series = valid_series.rank(method="first")

    if high_score_first:
        labels = np.linspace(5, 1, real_bins).round().astype(int).tolist()
    else:
        labels = np.linspace(1, 5, real_bins).round().astype(int).tolist()

    result.loc[valid_series.index] = pd.qcut(
        ranked_series,
        q=real_bins,
        labels=labels
    ).astype(float)

    return result.astype(float)


def add_rfm_scores(purchase_users, score_bins=5):
    """
    接口定义：
    输入：有购买行为的用户表，分箱数量
    输出：增加 R_score、F_score、M_score 后的用户表
    作用：计算 RFM 三个分数
    """
    purchase_users = purchase_users.copy()

    # R：最近一次购买距今越近越好，所以 days_since_last_purchase 越小分越高
    purchase_users["R_score"] = make_score_by_quantile(
        purchase_users["days_since_last_purchase"],
        score_bins=score_bins,
        high_score_first=True
    )

    # F：购买频率越高越好，这里沿用你原来的字段 purchase_day_frequency，数值越大分越高
    purchase_users["F_score"] = make_score_by_quantile(
        purchase_users["purchase_day_frequency"],
        score_bins=score_bins,
        high_score_first=False
    )

    # M：因为没有金额字段，所以用 purchase_count 代替，购买次数越多分越高
    purchase_users["M_score"] = make_score_by_quantile(
        purchase_users["purchase_count"],
        score_bins=score_bins,
        high_score_first=False
    )

    return purchase_users


def add_rfm_levels(purchase_users):
    """
    接口定义：
    输入：已经有 R/F/M 分数的用户表
    输出：增加 R_level、F_level、M_level 后的用户表
    作用：把分数转成“高/低”，方便分成 8 类用户
    """
    purchase_users = purchase_users.copy()

    r_mean = purchase_users["R_score"].mean()
    f_mean = purchase_users["F_score"].mean()
    m_mean = purchase_users["M_score"].mean()

    purchase_users["R_level"] = np.where(
        purchase_users["R_score"] > r_mean,
        "高",
        "低"
    )

    purchase_users["F_level"] = np.where(
        purchase_users["F_score"] > f_mean,
        "高",
        "低"
    )

    purchase_users["M_level"] = np.where(
        purchase_users["M_score"] > m_mean,
        "高",
        "低"
    )

    return purchase_users


def classify_rfm(row):
    """
    接口定义：
    输入：一行用户数据
    输出：这个用户所属的 RFM 类型
    作用：根据 R/F/M 的高低组合，把用户分成 8 类
    """
    r = row["R_level"]
    f = row["F_level"]
    m = row["M_level"]

    if r == "高" and f == "高" and m == "高":
        return "重要价值用户"
    elif r == "低" and f == "高" and m == "高":
        return "重要保持用户"
    elif r == "高" and f == "低" and m == "高":
        return "重要发展用户"
    elif r == "高" and f == "高" and m == "低":
        return "重要潜力用户"
    elif r == "高" and f == "低" and m == "低":
        return "一般价值用户"
    elif r == "低" and f == "高" and m == "低":
        return "一般保持用户"
    elif r == "低" and f == "低" and m == "高":
        return "一般发展用户"
    else:
        return "低价值用户"


def add_rfm_type(purchase_users):
    """
    接口定义：
    输入：已经有 R/F/M 高低标签的用户表
    输出：增加 rfm_type 后的用户表
    作用：生成最终用户类型
    """
    purchase_users = purchase_users.copy()

    purchase_users["rfm_type"] = purchase_users.apply(
        classify_rfm,
        axis=1
    )

    return purchase_users


def handle_non_purchase_users(non_purchase_users):
    """
    接口定义：
    输入：未购买用户表
    输出：补齐 RFM 字段后的未购买用户表
    作用：未购买用户没有购买时间、购买频率、购买次数，所以单独标记
    """
    non_purchase_users = non_purchase_users.copy()

    non_purchase_users["R_score"] = np.nan
    non_purchase_users["F_score"] = np.nan
    non_purchase_users["M_score"] = np.nan

    non_purchase_users["R_level"] = "未购买"
    non_purchase_users["F_level"] = "未购买"
    non_purchase_users["M_level"] = "未购买"

    non_purchase_users["rfm_type"] = "未购买用户"

    return non_purchase_users


def build_rfm_result(purchase_users, non_purchase_users, output_columns):
    """
    接口定义：
    输入：已购买用户表、未购买用户表、需要保留的列
    输出：最终用户级 RFM 结果表
    作用：把两类用户合并，并整理输出字段顺序
    """
    rfm_result = pd.concat(
        [purchase_users, non_purchase_users],
        ignore_index=True
    )

    existing_output_columns = [
        col for col in output_columns
        if col in rfm_result.columns
    ]

    rfm_result = rfm_result[existing_output_columns]

    return rfm_result


def build_rfm_summary(rfm_result, type_order):
    """
    接口定义：
    输入：用户级 RFM 结果表、用户类型排序规则
    输出：用户类型汇总表
    作用：统计每类用户数量、占比和平均指标
    """
    agg_rules = {
        "user_count": ("user_id", "count")
    }

    optional_agg_columns = {
        "avg_days_since_last_purchase": ("days_since_last_purchase", "mean"),
        "avg_purchase_day_frequency": ("purchase_day_frequency", "mean"),
        "avg_purchase_count": ("purchase_count", "mean"),
        "avg_purchase_rate": ("purchase_rate", "mean"),
        "avg_purchase_days": ("purchase_days", "mean")
    }

    for output_name, rule in optional_agg_columns.items():
        source_column = rule[0]
        if source_column in rfm_result.columns:
            agg_rules[output_name] = rule

    rfm_summary = (
        rfm_result
        .groupby("rfm_type")
        .agg(**agg_rules)
        .reset_index()
    )

    rfm_summary["user_rate"] = (
        rfm_summary["user_count"] / rfm_summary["user_count"].sum()
    ).round(4)

    rfm_summary["type_order"] = rfm_summary["rfm_type"].apply(
        lambda x: type_order.index(x) if x in type_order else 999
    )

    rfm_summary = (
        rfm_summary
        .sort_values("type_order")
        .drop(columns="type_order")
    )

    return rfm_summary


def save_results(rfm_result, rfm_summary, config):
    """
    接口定义：
    输入：用户级结果表、汇总表、配置字典
    输出：两个 csv 文件的保存路径
    作用：把最终结果保存到电脑文件夹中
    """
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    user_result_path = output_dir / config["user_result_filename"]
    summary_path = output_dir / config["summary_filename"]

    rfm_result.to_csv(
        user_result_path,
        index=False,
        encoding="utf-8-sig"
    )

    rfm_summary.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig"
    )

    return user_result_path, summary_path


def run_rfm_analysis(config):
    """
    接口定义：
    输入：
        config：配置字典，里面包含输入路径、输出路径、字段名、打分档数等参数
    输出：
        rfm_result：用户级 RFM 分层结果表
        rfm_summary：用户类型汇总表
        saved_paths：两个输出 csv 文件的路径

    """
    last_purchase, purchase_freq, purchase_value = load_data(config)

    df = merge_tables(
        last_purchase,
        purchase_freq,
        purchase_value,
        merge_key=config["merge_key"]
    )

    df = convert_numeric_columns(
        df,
        numeric_columns=config["numeric_columns"]
    )

    check_required_columns(
        df,
        required_columns=[
            config["merge_key"],
            "days_since_last_purchase",
            "purchase_day_frequency",
            "purchase_count"
        ]
    )

    purchase_users, non_purchase_users = split_purchase_users(df)

    purchase_users = add_rfm_scores(
        purchase_users,
        score_bins=config["score_bins"]
    )

    purchase_users = add_rfm_levels(purchase_users)
    purchase_users = add_rfm_type(purchase_users)

    non_purchase_users = handle_non_purchase_users(non_purchase_users)

    rfm_result = build_rfm_result(
        purchase_users,
        non_purchase_users,
        output_columns=config["output_columns"]
    )

    rfm_summary = build_rfm_summary(
        rfm_result,
        type_order=config["type_order"]
    )

    saved_paths = save_results(
        rfm_result,
        rfm_summary,
        config
    )

    return rfm_result, rfm_summary, saved_paths
