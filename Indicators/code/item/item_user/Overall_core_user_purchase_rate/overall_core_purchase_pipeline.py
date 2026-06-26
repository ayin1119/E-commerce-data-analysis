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
        读取 RFM 用户分层表，筛选出核心用户。
        本项目中，核心用户定义为 rfm_type = 重要价值用户。
    """
    user_col = config["user_col"]
    rfm_type_col = config["rfm_type_col"]
    core_user_type = config["core_user_type"]

    rfm = pd.read_csv(
        config["rfm_path"],
        usecols=[user_col, rfm_type_col],
        dtype={user_col: str}
    )

    core_users = (
        rfm[rfm[rfm_type_col] == core_user_type][user_col]
        .dropna()
        .drop_duplicates()
    )

    core_user_set = set(core_users)

    return core_user_set


def count_purchase_by_chunks(config, core_user_set):
    """
    接口定义：
    输入：
        config：配置参数字典
        core_user_set：核心用户 user_id 集合

    输出：
        total_purchase_count：全体购买次数
        core_user_purchase_count：核心用户购买次数

    作用：
        分块读取原始行为数据 data_min。
        只保留购买行为 behavior_type = 4。
        统计全体购买次数和核心用户购买次数。
    """
    user_col = config["user_col"]
    behavior_col = config["behavior_col"]
    purchase_behavior_value = config["purchase_behavior_value"]

    total_purchase_count = 0
    core_user_purchase_count = 0

    usecols = [
        user_col,
        behavior_col
    ]

    for chunk in pd.read_csv(
        config["data_path"],
        usecols=usecols,
        chunksize=config["chunksize"],
        dtype={user_col: str}
    ):
        # behavior_type 可能被读取成字符串，所以先统一转成数字
        chunk[behavior_col] = pd.to_numeric(
            chunk[behavior_col],
            errors="coerce"
        )

        # 只保留购买行为
        purchase_chunk = chunk[
            chunk[behavior_col] == purchase_behavior_value
        ]

        if purchase_chunk.empty:
            continue

        # 当前分块的购买总次数
        total_purchase_count += len(purchase_chunk)

        # 当前分块中，核心用户购买次数
        core_user_purchase_count += (
            purchase_chunk[user_col]
            .isin(core_user_set)
            .sum()
        )

    return total_purchase_count, core_user_purchase_count


def build_overall_result(total_purchase_count, core_user_purchase_count):
    """
    接口定义：
    输入：
        total_purchase_count：全体购买次数
        core_user_purchase_count：核心用户购买次数

    输出：
        result：整体核心用户购买率结果表

    作用：
        计算非核心用户购买次数和核心用户购买贡献率。
    """
    non_core_user_purchase_count = (
        total_purchase_count - core_user_purchase_count
    )

    if total_purchase_count == 0:
        core_user_purchase_rate = 0
        non_core_user_purchase_rate = 0
    else:
        core_user_purchase_rate = round(
            core_user_purchase_count / total_purchase_count,
            4
        )

        non_core_user_purchase_rate = round(
            non_core_user_purchase_count / total_purchase_count,
            4
        )

    result = pd.DataFrame([
        {
            "total_purchase_count": total_purchase_count,
            "core_user_purchase_count": core_user_purchase_count,
            "non_core_user_purchase_count": non_core_user_purchase_count,
            "core_user_purchase_rate": core_user_purchase_rate,
            "non_core_user_purchase_rate": non_core_user_purchase_rate
        }
    ])

    return result


def save_result(result, config):
    """
    接口定义：
    输入：
        result：整体核心用户购买率结果表
        config：配置参数字典

    输出：
        output_path：结果保存路径

    作用：
        将结果保存为 CSV 文件。
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


def run_overall_core_purchase_analysis(config):
    """
    统一接口定义：
    输入：
        config：配置参数字典

    输出：
        result：整体核心用户购买率结果表
        output_path：结果保存路径

    作用：
        外部只需要调用这个函数，就可以完成完整分析流程。
    """
    core_user_set = load_core_users(config)

    total_purchase_count, core_user_purchase_count = count_purchase_by_chunks(
        config,
        core_user_set
    )

    result = build_overall_result(
        total_purchase_count,
        core_user_purchase_count
    )

    output_path = save_result(
        result,
        config
    )

    return result, output_path