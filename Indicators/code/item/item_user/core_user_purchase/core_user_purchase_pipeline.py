from pathlib import Path
import pandas as pd


def load_core_users(config):
    """
    接口定义：
    输入：
        config：配置参数字典

    输出：
        core_user_set：核心用户 user_id 集合

    作用：
        读取 RFM 用户分层结果表，筛选出核心用户。
    """
    user_col = config["user_col"]
    rfm_type_col = config["rfm_type_col"]
    core_user_type = config["core_user_type"]

    rfm = pd.read_csv(
        config["rfm_path"],
        usecols=[user_col, rfm_type_col],
        dtype={user_col: str}
    )

    core_users = rfm[
        rfm[rfm_type_col] == core_user_type
    ][user_col].dropna().drop_duplicates()

    core_user_set = set(core_users)

    return core_user_set


def process_purchase_chunks(config, core_user_set):
    """
    接口定义：
    输入：
        config：配置参数字典
        core_user_set：核心用户 user_id 集合

    输出：
        item_purchase_count：商品购买统计表

    作用：
        分块读取原始行为数据 data_min。
        只保留购买行为 behavior_type = 4。
        按 item_category + item_id 统计：
            total_purchase_count：总购买次数
            core_user_purchase_count：核心用户购买次数
    """
    user_col = config["user_col"]
    item_col = config["item_col"]
    category_col = config["category_col"]
    behavior_col = config["behavior_col"]
    purchase_behavior_value = config["purchase_behavior_value"]

    usecols = [
        user_col,
        item_col,
        category_col,
        behavior_col
    ]

    result_parts = []

    for chunk in pd.read_csv(
        config["data_path"],
        usecols=usecols,
        chunksize=config["chunksize"],
        dtype={
            user_col: str,
            item_col: str
        }
    ):
        # behavior_type 可能被读成字符串，所以这里统一转成数字
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

        # 去掉关键字段为空的数据
        purchase_chunk = purchase_chunk.dropna(
            subset=[user_col, item_col, category_col]
        )

        if purchase_chunk.empty:
            continue

        # 判断该购买行为是否来自核心用户
        # 这里没有整表 merge，而是用 isin 判断 user_id 是否在核心用户集合里
        purchase_chunk["is_core_user"] = (
            purchase_chunk[user_col].isin(core_user_set)
        )

        # 当前分块内，按商品类别 + 商品ID 统计
        chunk_result = (
            purchase_chunk
            .groupby([category_col, item_col])
            .agg(
                total_purchase_count=(user_col, "count"),
                core_user_purchase_count=("is_core_user", "sum")
            )
            .reset_index()
        )

        result_parts.append(chunk_result)

    # 如果没有购买数据，返回空表，避免程序报错
    if not result_parts:
        return pd.DataFrame(
            columns=[
                category_col,
                item_col,
                "total_purchase_count",
                "core_user_purchase_count"
            ]
        )

    # 合并所有分块的统计结果
    item_purchase_count = (
        pd.concat(result_parts, ignore_index=True)
        .groupby([category_col, item_col], as_index=False)
        .agg(
            total_purchase_count=("total_purchase_count", "sum"),
            core_user_purchase_count=("core_user_purchase_count", "sum")
        )
    )

    return item_purchase_count


def calculate_core_purchase_rate(item_purchase_count):
    """
    接口定义：
    输入：
        item_purchase_count：商品购买统计表

    输出：
        item_core_purchase：增加核心用户购买率后的结果表

    作用：
        计算：
            非核心用户购买次数
            核心用户购买率

        核心用户购买率 = 核心用户购买次数 / 总购买次数
    """
    item_core_purchase = item_purchase_count.copy()

    if item_core_purchase.empty:
        return item_core_purchase

    item_core_purchase["non_core_user_purchase_count"] = (
        item_core_purchase["total_purchase_count"]
        - item_core_purchase["core_user_purchase_count"]
    )

    item_core_purchase["core_user_purchase_rate"] = (
        item_core_purchase["core_user_purchase_count"]
        / item_core_purchase["total_purchase_count"]
    ).round(4)

    return item_core_purchase


def sort_result_if_needed(item_core_purchase, config):
    """
    接口定义：
    输入：
        item_core_purchase：商品核心用户购买率结果表
        config：配置参数字典

    输出：
        排序后或未排序的结果表

    作用：
        根据 config.py 里的 sort_result 参数决定是否排序。

        如果 sort_result = False：
            不做全量排序，时间复杂度更低。

        如果 sort_result = True：
            按商品类别、核心用户购买率、总购买次数排序，结果更方便查看。
    """
    if item_core_purchase.empty:
        return item_core_purchase

    if not config["sort_result"]:
        return item_core_purchase

    category_col = config["category_col"]

    item_core_purchase = item_core_purchase.sort_values(
        by=[
            category_col,
            "core_user_purchase_rate",
            "total_purchase_count"
        ],
        ascending=[
            True,
            False,
            False
        ]
    )

    return item_core_purchase


def save_result(item_core_purchase, config):
    """
    接口定义：
    输入：
        item_core_purchase：最终结果表
        config：配置参数字典

    输出：
        output_path：结果保存路径

    作用：
        将结果保存成 CSV 文件。
    """
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / config["output_filename"]

    item_core_purchase.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    return output_path


def run_core_user_purchase_analysis(config):
    """
    统一接口定义：
    输入：
        config：配置参数字典

    输出：
        item_core_purchase：商品核心用户购买率结果表
        output_path：结果保存路径

    作用：
        外部只需要调用这个函数，就可以完成完整分析流程。
    """
    core_user_set = load_core_users(config)

    item_purchase_count = process_purchase_chunks(
        config,
        core_user_set
    )

    item_core_purchase = calculate_core_purchase_rate(
        item_purchase_count
    )

    item_core_purchase = sort_result_if_needed(
        item_core_purchase,
        config
    )

    output_path = save_result(
        item_core_purchase,
        config
    )

    return item_core_purchase, output_path