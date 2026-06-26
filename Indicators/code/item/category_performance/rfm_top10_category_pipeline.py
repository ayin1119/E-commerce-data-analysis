from pathlib import Path
import pandas as pd


def load_rfm_user_segment(config):
    """
    接口定义：
    输入：config 配置字典
    输出：RFM 用户分层表

    作用：
    读取 RFM 用户分层结果，只保留 user_id 和 rfm_type 两列。
    """
    user_col = config["user_col"]
    rfm_type_col = config["rfm_type_col"]

    rfm = pd.read_csv(
        config["rfm_path"],
        usecols=[user_col, rfm_type_col],
        dtype={user_col: str}
    )

    # 去掉 user_id 为空的数据
    rfm = rfm.dropna(subset=[user_col])

    # 如果同一个 user_id 出现多次，只保留第一条
    rfm = rfm.drop_duplicates(subset=[user_col])

    return rfm


def process_purchase_chunks(config, rfm):
    """
    接口定义：
    输入：
        config：配置字典
        rfm：RFM 用户分层表

    输出：
        purchase_count_df：每个 RFM 层级下，每个商品类别的购买次数
        user_category_pairs：用户-层级-类别的去重表

    作用：
    分块读取原始行为数据 data_min。
    只保留购买行为 behavior_type = 4。
    然后和 RFM 用户分层表合并，统计每个层级下的购买类别。
    """
    user_col = config["user_col"]
    category_col = config["category_col"]
    behavior_col = config["behavior_col"]
    rfm_type_col = config["rfm_type_col"]
    purchase_behavior_value = config["purchase_behavior_value"]

    purchase_count_parts = []
    user_category_pair_parts = []

    usecols = [
        user_col,
        category_col,
        behavior_col
    ]

    for chunk in pd.read_csv(
        config["data_path"],
        usecols=usecols,
        chunksize=config["chunksize"],
        dtype={user_col: str}
    ):
        # behavior_type 可能被读成字符串，所以先转成数字
        chunk[behavior_col] = pd.to_numeric(
            chunk[behavior_col],
            errors="coerce"
        )

        # 只保留购买行为
        purchase_chunk = chunk[
            chunk[behavior_col] == purchase_behavior_value
        ].copy()

        if purchase_chunk.empty:
            continue

        # 只保留后面要用的列
        purchase_chunk = purchase_chunk[
            [user_col, category_col]
        ]

        # 和 RFM 用户分层表合并，得到每个购买用户属于哪个 RFM 层级
        purchase_with_rfm = purchase_chunk.merge(
            rfm,
            on=user_col,
            how="inner"
        )

        if purchase_with_rfm.empty:
            continue

        # 去掉类别为空或 RFM 类型为空的数据
        purchase_with_rfm = purchase_with_rfm.dropna(
            subset=[category_col, rfm_type_col]
        )

        if purchase_with_rfm.empty:
            continue

        # 统计当前分块里，每个 RFM 层级 + 商品类别的购买次数
        chunk_purchase_count = (
            purchase_with_rfm
            .groupby([rfm_type_col, category_col])
            .size()
            .reset_index(name="purchase_count")
        )

        purchase_count_parts.append(chunk_purchase_count)

        # 保存用户-层级-类别去重关系，用于后面计算购买用户数
        chunk_user_category_pairs = (
            purchase_with_rfm[
                [user_col, rfm_type_col, category_col]
            ]
            .drop_duplicates()
        )

        user_category_pair_parts.append(chunk_user_category_pairs)

    # 如果没有任何购买数据，返回空表，避免程序报错
    if not purchase_count_parts:
        purchase_count_df = pd.DataFrame(
            columns=[rfm_type_col, category_col, "purchase_count"]
        )

        user_category_pairs = pd.DataFrame(
            columns=[user_col, rfm_type_col, category_col]
        )

        return purchase_count_df, user_category_pairs

    # 把所有分块统计结果合并
    purchase_count_df = (
        pd.concat(purchase_count_parts, ignore_index=True)
        .groupby([rfm_type_col, category_col], as_index=False)["purchase_count"]
        .sum()
    )

    # 用户-层级-类别关系需要再次去重
    # 因为同一个用户可能在不同分块中购买过同一类商品
    user_category_pairs = (
        pd.concat(user_category_pair_parts, ignore_index=True)
        .drop_duplicates()
    )

    return purchase_count_df, user_category_pairs


def build_category_summary(purchase_count_df, user_category_pairs, config):
    """
    接口定义：
    输入：
        purchase_count_df：类别购买次数表
        user_category_pairs：用户-层级-类别去重表
        config：配置字典

    输出：
        category_summary：每个 RFM 层级下，每个商品类别的统计结果

    作用：
    计算每个类别的购买次数、购买用户数、购买次数占比、购买用户占比。
    """
    user_col = config["user_col"]
    category_col = config["category_col"]
    rfm_type_col = config["rfm_type_col"]

    if purchase_count_df.empty:
        return pd.DataFrame()

    # 计算每个 RFM 层级 + 商品类别有多少个购买用户
    category_user_count = (
        user_category_pairs
        .groupby([rfm_type_col, category_col])
        .size()
        .reset_index(name="purchase_user_count")
    )

    # 计算每个 RFM 层级的总购买次数
    rfm_total_purchase_count = (
        purchase_count_df
        .groupby(rfm_type_col)["purchase_count"]
        .sum()
        .reset_index(name="rfm_total_purchase_count")
    )

    # 计算每个 RFM 层级的购买用户总数
    rfm_purchase_user_count = (
        user_category_pairs[[rfm_type_col, user_col]]
        .drop_duplicates()
        .groupby(rfm_type_col)
        .size()
        .reset_index(name="rfm_purchase_user_count")
    )

    # 合并统计结果
    category_summary = purchase_count_df.merge(
        category_user_count,
        on=[rfm_type_col, category_col],
        how="left"
    )

    category_summary = category_summary.merge(
        rfm_total_purchase_count,
        on=rfm_type_col,
        how="left"
    )

    category_summary = category_summary.merge(
        rfm_purchase_user_count,
        on=rfm_type_col,
        how="left"
    )

    # 购买次数占比 = 某类别购买次数 / 该 RFM 层级总购买次数
    category_summary["purchase_count_rate"] = (
        category_summary["purchase_count"]
        / category_summary["rfm_total_purchase_count"]
    ).round(4)

    # 购买用户占比 = 买过该类别的用户数 / 该 RFM 层级购买用户总数
    category_summary["purchase_user_rate"] = (
        category_summary["purchase_user_count"]
        / category_summary["rfm_purchase_user_count"]
    ).round(4)

    return category_summary


def get_top_k_categories(category_summary, config):
    """
    接口定义：
    输入：
        category_summary：商品类别汇总表
        config：配置字典

    输出：
        每个 RFM 层级购买次数最高的 TopK 商品类别

    作用：
    不再对所有类别完整排序，而是每个 RFM 层级只取前 K 个。
    """
    rfm_type_col = config["rfm_type_col"]
    top_k = config["top_k"]

    if category_summary.empty:
        return category_summary

    # groupby + nlargest 表示：
    # 每个 RFM 层级内部，只取 purchase_count 最大的前 K 个
    top_index = (
        category_summary
        .groupby(rfm_type_col)["purchase_count"]
        .nlargest(top_k)
        .index
        .get_level_values(-1)
    )

    top_result = category_summary.loc[top_index].copy()

    # 这里只对已经选出来的 TopK 做小范围排序
    # 不是对全部类别做完整排序
    top_result = top_result.sort_values(
        by=[rfm_type_col, "purchase_count", "purchase_user_count"],
        ascending=[True, False, False]
    )

    top_result["category_rank"] = (
        top_result
        .groupby(rfm_type_col)
        .cumcount() + 1
    )

    output_cols = [
        rfm_type_col,
        "category_rank",
        config["category_col"],
        "purchase_count",
        "purchase_user_count",
        "rfm_total_purchase_count",
        "rfm_purchase_user_count",
        "purchase_count_rate",
        "purchase_user_rate"
    ]

    return top_result[output_cols]


def save_result(result, config):
    """
    接口定义：
    输入：
        result：最终结果表
        config：配置字典

    输出：
        output_path：保存文件路径

    作用：
    把最终结果保存成 CSV 文件。
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


def run_rfm_top10_category_analysis(config):
    """
    统一接口定义：
    输入：
        config：配置参数字典

    输出：
        result：每个 RFM 层级的 Top10 商品类别结果
        output_path：结果保存路径

    作用：
    外部只需要调用这个函数，就可以完成完整分析流程。
    """
    rfm = load_rfm_user_segment(config)

    purchase_count_df, user_category_pairs = process_purchase_chunks(
        config,
        rfm
    )

    category_summary = build_category_summary(
        purchase_count_df,
        user_category_pairs,
        config
    )

    result = get_top_k_categories(
        category_summary,
        config
    )

    output_path = save_result(
        result,
        config
    )

    return result, output_path