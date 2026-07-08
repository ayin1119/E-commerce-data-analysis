from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(
    page_title="电商购买概率预测仪表盘",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"

PROBA_COLS = {
    "original": {
        "label": "Original 原始概率",
        "column": "original_xgb_probability",
        "note": "未校准的 XGBoost 原始输出概率，排序能力强，但概率值整体偏高。",
    },
    "platt": {
        "label": "Platt 校准概率",
        "column": "platt_xgb_probability",
        "note": "经过 Platt Scaling 校准，概率均值更接近真实购买率，适合业务概率解释。",
    },
    "isotonic": {
        "label": "Isotonic 校准概率",
        "column": "isotonic_xgb_probability",
        "note": "经过 Isotonic Regression 校准，适合观察校准效果，但可能略影响排序稳定性。",
    },
}


def pct(value: float, digits: int = 2) -> str:
    if pd.isna(value):
        return "-"
    return f"{value * 100:.{digits}f}%"


def num(value, digits: int = 4) -> str:
    if pd.isna(value):
        return "-"
    if isinstance(value, (int, np.integer)):
        return f"{int(value):,}"
    return f"{float(value):.{digits}f}"


@st.cache_data
def load_data():
    pred = pd.read_csv(DATA_DIR / "predictions.csv")
    metrics = pd.read_csv(DATA_DIR / "calibration_metrics.csv")
    bins = pd.read_csv(DATA_DIR / "calibration_bin_report.csv")
    top = pd.read_csv(DATA_DIR / "top_rate_metrics.csv")
    model_compare = pd.read_csv(DATA_DIR / "model_comparison_from_report.csv")
    feature_expl = pd.read_csv(DATA_DIR / "feature_explanation_from_report.csv")

    pred["snapshot_date"] = pd.to_datetime(pred["snapshot_date"], errors="coerce")
    for c in [
        "xgb_probability",
        "original_xgb_probability",
        "platt_xgb_probability",
        "isotonic_xgb_probability",
    ]:
        if c in pred.columns:
            pred[c] = pd.to_numeric(pred[c], errors="coerce")

    return pred, metrics, bins, top, model_compare, feature_expl


def get_metric_row(metrics: pd.DataFrame, split: str, method: str) -> pd.Series:
    row = metrics[(metrics["split"] == split) & (metrics["method"] == method)]
    if row.empty:
        return pd.Series(dtype="object")
    return row.iloc[0]


def method_col(method: str) -> str:
    return PROBA_COLS[method]["column"]


def unique_existing_cols(cols, data: pd.DataFrame) -> list:
    """
    保留实际存在的列，并去掉重复列名。
    解决 selected_col 与固定概率列重复导致的 Streamlit / PyArrow 报错。
    """
    clean_data = data.loc[:, ~data.columns.duplicated()]
    existing = set(clean_data.columns)
    result = []

    for c in cols:
        if c in existing and c not in result:
            result.append(c)

    return result


def make_display_df(data: pd.DataFrame, cols=None, n=None) -> pd.DataFrame:
    """
    在 st.dataframe() 或导出 CSV 前统一清理：
    1. 去掉 DataFrame 本身的重复列
    2. 去掉 show_cols 里的重复列
    3. 只保留实际存在的列
    4. 可选截取前 n 行
    """
    clean_data = data.loc[:, ~data.columns.duplicated()].copy()

    if cols is not None:
        clean_cols = unique_existing_cols(cols, clean_data)
        clean_data = clean_data.loc[:, clean_cols].copy()

    if n is not None:
        clean_data = clean_data.head(n)

    return clean_data


@st.cache_data(show_spinner=False)
def compute_top_curve(pred: pd.DataFrame, split: str, method: str, max_percent: int = 30) -> pd.DataFrame:
    col = method_col(method)
    df = pred[pred["dataset_type"] == split].copy()
    df = df.sort_values(col, ascending=False).reset_index(drop=True)
    total_pos = max(int(df["label_buy_7d"].sum()), 1)
    rows = []
    for p in range(1, max_percent + 1):
        n = max(1, int(len(df) * p / 100))
        selected = df.iloc[:n]
        tp = int(selected["label_buy_7d"].sum())
        rows.append(
            {
                "top_percent": p,
                "top_n": n,
                "threshold": float(selected[col].min()),
                "precision": tp / n,
                "recall": tp / total_pos,
                "purchase_count": tp,
            }
        )
    return pd.DataFrame(rows)


def compute_topk(pred: pd.DataFrame, split: str, method: str, top_percent: int):
    col = method_col(method)
    df = pred[pred["dataset_type"] == split].copy()
    df = df.sort_values(col, ascending=False).reset_index(drop=True)
    n = max(1, int(len(df) * top_percent / 100))
    selected = df.iloc[:n].copy()
    rest = df.iloc[n:].copy()

    total_pos = int(df["label_buy_7d"].sum())
    total_neg = len(df) - total_pos
    tp = int(selected["label_buy_7d"].sum())
    fp = n - tp
    fn = total_pos - tp
    tn = len(df) - n - fn
    threshold = float(selected[col].min())

    stats = {
        "top_n": n,
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": tp / n if n else np.nan,
        "recall": tp / total_pos if total_pos else np.nan,
        "total_pos": total_pos,
        "total_neg": total_neg,
        "sample_count": len(df),
    }
    return selected, rest, stats


def make_confusion_fig(stats: dict):
    z = [[stats["tn"], stats["fp"]], [stats["fn"], stats["tp"]]]
    text = [
        [f"TN<br>{stats['tn']:,}", f"FP<br>{stats['fp']:,}"],
        [f"FN<br>{stats['fn']:,}", f"TP<br>{stats['tp']:,}"],
    ]
    fig = go.Figure(
        data=go.Heatmap(
            z=z,
            x=["预测低分", "预测高分"],
            y=["真实未购买", "真实购买"],
            text=text,
            texttemplate="%{text}",
            hovertemplate="%{y} / %{x}<br>样本数=%{z:,}<extra></extra>",
        )
    )
    fig.update_layout(
        height=420,
        margin=dict(l=30, r=30, t=40, b=30),
        title="Top-K 口径下的混淆矩阵",
    )
    return fig


def probability_histogram(pred: pd.DataFrame, split: str):
    df = pred[pred["dataset_type"] == split]
    rows = []
    bins = np.linspace(0, 1, 21)
    labels = [f"{bins[i]:.2f}-{bins[i+1]:.2f}" for i in range(len(bins) - 1)]

    for method, meta in PROBA_COLS.items():
        col = meta["column"]
        counts, _ = np.histogram(df[col].dropna(), bins=bins)
        for label, count in zip(labels, counts):
            rows.append(
                {
                    "概率区间": label,
                    "样本数": int(count),
                    "method": method,
                    "method_label": meta["label"],
                }
            )
    return pd.DataFrame(rows)


pred, metrics, bins, top_rates, model_compare, feature_expl = load_data()

st.title("🛒 电商用户-商品 7 天购买概率预测仪表盘")
st.caption(
    "基于 XGBoost 购买概率预测结果，展示模型效果、Top-K 候选池、概率校准、错误样本和业务解释。"
)

with st.sidebar:
    st.header("筛选控制")
    page = st.radio(
        "页面",
        [
            "1. 项目总览",
            "2. Top-K 业务筛选",
            "3. 概率校准分析",
            "4. 错误样本分析",
            "5. 预测明细查询",
            "6. 使用说明",
        ],
        label_visibility="collapsed",
    )

    split = st.selectbox("数据集", sorted(pred["dataset_type"].dropna().unique()), index=sorted(pred["dataset_type"].dropna().unique()).index("test") if "test" in pred["dataset_type"].unique() else 0)
    method = st.selectbox(
        "概率版本",
        list(PROBA_COLS.keys()),
        index=1,
        format_func=lambda x: PROBA_COLS[x]["label"],
    )
    top_percent = st.slider("Top 候选池比例", min_value=1, max_value=30, value=10, step=1)
    st.info(PROBA_COLS[method]["note"])

selected_col = method_col(method)
selected_metrics = get_metric_row(metrics, split, method)
top_selected, rest_selected, top_stats = compute_topk(pred, split, method, top_percent)


if page == "1. 项目总览":
    st.subheader("项目核心结论")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("样本数", f"{int(selected_metrics.get('sample_count', len(pred[pred['dataset_type'] == split]))):,}")
    c2.metric("真实购买率", pct(selected_metrics.get("positive_rate", np.nan)))
    c3.metric("AUC", num(selected_metrics.get("auc", np.nan)))
    c4.metric("PR-AUC", num(selected_metrics.get("pr_auc", np.nan)))
    c5.metric("ECE", num(selected_metrics.get("ece_10bins", np.nan)))

    c6, c7, c8, c9 = st.columns(4)
    c6.metric(f"Top{top_percent}% 样本数", f"{top_stats['top_n']:,}")
    c7.metric(f"Top{top_percent}% 购买率", pct(top_stats["precision"]))
    c8.metric(f"Top{top_percent}% 召回率", pct(top_stats["recall"]))
    c9.metric("当前概率阈值", num(top_stats["threshold"], 4))

    st.markdown(
        """
        这个仪表盘的重点不是重新训练模型，而是把已经训练好的 XGBoost 结果转化为业务可用的筛选工具。
        使用者可以通过左侧选择数据集、概率校准方法和 Top 候选池比例，实时观察购买率、召回率、阈值和候选样本变化。
        """
    )

    st.divider()
    st.subheader("报告中的模型效果对比")

    display_cols = [
        "rank",
        "model",
        "experiment_version",
        "feature_count",
        "valid_pr_auc",
        "test_auc",
        "test_pr_auc",
        "test_top10_purchase_rate",
        "test_top10_recall",
        "train_time_sec",
    ]

    table = model_compare[display_cols].copy()
    st.dataframe(
        table.style.format(
            {
                "valid_pr_auc": "{:.4f}",
                "test_auc": "{:.4f}",
                "test_pr_auc": "{:.4f}",
                "test_top10_purchase_rate": "{:.2%}",
                "test_top10_recall": "{:.2%}",
                "train_time_sec": "{:.2f}s",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    fig = px.bar(
        model_compare.sort_values("test_pr_auc", ascending=True),
        x="test_pr_auc",
        y="experiment_version",
        color="model",
        orientation="h",
        text="test_pr_auc",
        title="不同模型 Test PR-AUC 对比",
        labels={"test_pr_auc": "Test PR-AUC", "experiment_version": "实验版本"},
    )
    fig.update_traces(texttemplate="%{text:.4f}", textposition="outside")
    fig.update_layout(height=500, xaxis_range=[0, max(model_compare["test_pr_auc"]) * 1.12])
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.bar(
        model_compare.sort_values("test_top10_purchase_rate", ascending=True),
        x="test_top10_purchase_rate",
        y="experiment_version",
        color="model",
        orientation="h",
        text="test_top10_purchase_rate",
        title="不同模型 Test Top10% 购买率对比",
        labels={"test_top10_purchase_rate": "Test Top10% 购买率", "experiment_version": "实验版本"},
    )
    fig2.update_traces(texttemplate="%{text:.2%}", textposition="outside")
    fig2.update_layout(height=500, xaxis_tickformat=".0%")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("特征业务解释")
    st.dataframe(feature_expl, use_container_width=True, hide_index=True)


elif page == "2. Top-K 业务筛选":
    st.subheader("Top-K 高购买概率候选池")

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("候选池比例", f"Top {top_percent}%")
    c2.metric("候选样本数", f"{top_stats['top_n']:,}")
    c3.metric("概率阈值", num(top_stats["threshold"], 4))
    c4.metric("候选池购买率", pct(top_stats["precision"]))
    c5.metric("真实购买召回率", pct(top_stats["recall"]))

    st.markdown(
        """
        这一页用于模拟推荐或营销触达场景。Top 比例越小，候选池通常越精准；Top 比例越大，覆盖的真实购买用户越多。
        可以用这个页面决定“只触达最可能购买的前多少用户-商品组合”。
        """
    )

    curve = compute_top_curve(pred, split, method, max_percent=30)
    curve_long = curve.melt(
        id_vars=["top_percent", "top_n", "threshold", "purchase_count"],
        value_vars=["precision", "recall"],
        var_name="指标",
        value_name="数值",
    )
    curve_long["指标"] = curve_long["指标"].map({"precision": "Top-K 购买率 / Precision", "recall": "Top-K 召回率 / Recall"})

    fig = px.line(
        curve_long,
        x="top_percent",
        y="数值",
        color="指标",
        markers=True,
        title=f"{split} 集：Top 比例变化下的购买率和召回率",
        labels={"top_percent": "Top 候选池比例（%）", "数值": "指标值"},
        hover_data={"top_n": ":,", "threshold": ":.4f", "purchase_count": ":,"},
    )
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    fig_threshold = px.line(
        curve,
        x="top_percent",
        y="threshold",
        markers=True,
        title="Top 比例变化下的概率阈值",
        labels={"top_percent": "Top 候选池比例（%）", "threshold": "最低入选概率阈值"},
        hover_data={"top_n": ":,", "purchase_count": ":,"},
    )
    st.plotly_chart(fig_threshold, use_container_width=True)

    st.subheader("当前 Top 候选用户-商品明细")
    show_cols = [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d",
        selected_col,
        "original_xgb_probability",
        "platt_xgb_probability",
        "isotonic_xgb_probability",
    ]
    show_cols = unique_existing_cols(show_cols, top_selected)
    st.dataframe(make_display_df(top_selected, show_cols, 500), use_container_width=True, hide_index=True)

    csv = make_display_df(top_selected, show_cols).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="下载当前 Top 候选池 CSV",
        data=csv,
        file_name=f"top{top_percent}_{split}_{method}_candidates.csv",
        mime="text/csv",
    )


elif page == "3. 概率校准分析":
    st.subheader("概率校准指标")

    st.markdown(
        """
        同一个 XGBoost 排序模型可以输出不同概率版本。Original 适合看排序能力，但概率均值容易偏高；
        Platt 和 Isotonic 用于把模型分数校准到更接近真实购买率的概率。
        """
    )

    split_metrics = metrics[metrics["split"] == split].copy()
    st.dataframe(
        split_metrics.style.format(
            {
                "positive_rate": "{:.2%}",
                "auc": "{:.4f}",
                "pr_auc": "{:.4f}",
                "brier_score": "{:.4f}",
                "log_loss": "{:.4f}",
                "ece_10bins": "{:.4f}",
                "mce_10bins": "{:.4f}",
                "mean_predicted_probability": "{:.2%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(
            split_metrics,
            x="method",
            y=["brier_score", "log_loss", "ece_10bins"],
            barmode="group",
            title=f"{split} 集：校准误差指标对比（越低越好）",
            labels={"value": "指标值", "variable": "指标", "method": "概率版本"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        compare_df = split_metrics[["method", "positive_rate", "mean_predicted_probability"]].melt(
            id_vars="method",
            var_name="指标",
            value_name="概率",
        )
        compare_df["指标"] = compare_df["指标"].map(
            {"positive_rate": "真实购买率", "mean_predicted_probability": "平均预测概率"}
        )
        fig = px.bar(
            compare_df,
            x="method",
            y="概率",
            color="指标",
            barmode="group",
            title=f"{split} 集：平均预测概率 vs 真实购买率",
            labels={"概率": "概率", "method": "概率版本"},
        )
        fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Reliability Curve / 分箱校准曲线")
    bin_split = bins[bins["split"] == split].copy()
    fig = go.Figure()
    for m, mdf in bin_split.groupby("method"):
        label = PROBA_COLS.get(m, {}).get("label", m)
        fig.add_trace(
            go.Scatter(
                x=mdf["mean_predicted_probability"],
                y=mdf["actual_purchase_rate"],
                mode="lines+markers",
                name=label,
                hovertemplate="平均预测概率=%{x:.2%}<br>真实购买率=%{y:.2%}<extra></extra>",
            )
        )
    fig.add_trace(
        go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode="lines",
            name="完美校准线",
            line=dict(dash="dash"),
            hoverinfo="skip",
        )
    )
    fig.update_layout(
        title=f"{split} 集：预测概率与真实购买率对比",
        xaxis_title="分箱平均预测概率",
        yaxis_title="分箱真实购买率",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        height=560,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("预测概率分布")
    hist_df = probability_histogram(pred, split)
    fig = px.bar(
        hist_df,
        x="概率区间",
        y="样本数",
        color="method_label",
        barmode="group",
        title=f"{split} 集：不同概率版本的预测概率分布",
        labels={"method_label": "概率版本"},
    )
    st.plotly_chart(fig, use_container_width=True)


elif page == "4. 错误样本分析":
    st.subheader("Top-K 口径下的错误分析")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TP 高分且购买", f"{top_stats['tp']:,}")
    c2.metric("FP 高分未购买", f"{top_stats['fp']:,}")
    c3.metric("FN 低分但购买", f"{top_stats['fn']:,}")
    c4.metric("TN 低分未购买", f"{top_stats['tn']:,}")

    st.plotly_chart(make_confusion_fig(top_stats), use_container_width=True)

    st.markdown(
        """
        FP 表示模型认为购买概率高，但标签窗口内没有购买；这类样本可能是用户兴趣强但最终放弃、购买发生在窗口外，或者被其他商品分流。
        FN 表示模型给了较低概率，但用户实际购买；这类样本常见于购买决策很快、前置行为短，或者关键行为没有落在观察窗口内。
        """
    )

    fp_table = top_selected[top_selected["label_buy_7d"] == 0].sort_values(selected_col, ascending=False).copy()
    fn_table = rest_selected[rest_selected["label_buy_7d"] == 1].sort_values(selected_col, ascending=True).copy()

    show_cols = [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d",
        selected_col,
        "original_xgb_probability",
        "platt_xgb_probability",
        "isotonic_xgb_probability",
    ]
    show_cols = unique_existing_cols(show_cols, pred)

    tab1, tab2 = st.tabs(["FP：高分未购买", "FN：低分实际购买"])
    with tab1:
        st.dataframe(make_display_df(fp_table, show_cols, 300), use_container_width=True, hide_index=True)
        csv = make_display_df(fp_table, show_cols).to_csv(index=False).encode("utf-8-sig")
        st.download_button("下载 FP 错误样本", csv, f"fp_{split}_{method}_top{top_percent}.csv", "text/csv")

    with tab2:
        st.dataframe(make_display_df(fn_table, show_cols, 300), use_container_width=True, hide_index=True)
        csv = make_display_df(fn_table, show_cols).to_csv(index=False).encode("utf-8-sig")
        st.download_button("下载 FN 错误样本", csv, f"fn_{split}_{method}_top{top_percent}.csv", "text/csv")


elif page == "5. 预测明细查询":
    st.subheader("预测明细查询与下载")

    df = pred[pred["dataset_type"] == split].copy()

    c1, c2, c3 = st.columns(3)
    with c1:
        label_filter = st.selectbox("真实标签", ["全部", "购买 label=1", "未购买 label=0"])
    with c2:
        min_prob, max_prob = st.slider(
            "概率范围",
            min_value=0.0,
            max_value=1.0,
            value=(0.0, 1.0),
            step=0.01,
        )
    with c3:
        category_text = st.text_input("商品类别筛选，可输入多个，用英文逗号分隔", "")

    if label_filter == "购买 label=1":
        df = df[df["label_buy_7d"] == 1]
    elif label_filter == "未购买 label=0":
        df = df[df["label_buy_7d"] == 0]

    df = df[(df[selected_col] >= min_prob) & (df[selected_col] <= max_prob)]

    if category_text.strip():
        try:
            cats = [int(x.strip()) for x in category_text.split(",") if x.strip()]
            df = df[df["item_category"].isin(cats)]
        except ValueError:
            st.warning("商品类别需要输入数字，例如：5399,13230,3628")

    sort_ascending = st.checkbox("按概率从低到高排序", value=False)
    df = df.sort_values(selected_col, ascending=sort_ascending)

    st.write(f"筛选后样本数：**{len(df):,}**")
    show_cols = [
        "dataset_type",
        "snapshot_date",
        "user_id",
        "item_id",
        "item_category",
        "label_buy_7d",
        selected_col,
        "original_xgb_probability",
        "platt_xgb_probability",
        "isotonic_xgb_probability",
    ]
    show_cols = unique_existing_cols(show_cols, df)
    st.dataframe(make_display_df(df, show_cols, 1000), use_container_width=True, hide_index=True)

    csv = make_display_df(df, show_cols).to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "下载当前筛选结果 CSV",
        csv,
        f"filtered_predictions_{split}_{method}.csv",
        "text/csv",
    )


elif page == "6. 使用说明":
    st.subheader("仪表盘使用说明")

    st.markdown(
        """
        ### 1. 运行方式

        在项目文件夹中打开终端，执行：

        ```bash
        pip install -r requirements.txt
        streamlit run app.py
        ```

        如果你使用 Mac，也可以双击 `run_dashboard_mac.command`，它会自动安装依赖并启动仪表盘。

        ### 2. 页面说明

        - **项目总览**：展示样本数、真实购买率、AUC、PR-AUC、ECE，以及报告中的模型对比结果。
        - **Top-K 业务筛选**：通过滑动 Top 比例，查看候选池购买率、召回率、概率阈值和候选用户商品明细。
        - **概率校准分析**：对比 Original、Platt、Isotonic 三种概率版本的 Brier Score、Log Loss、ECE 和校准曲线。
        - **错误样本分析**：在 Top-K 口径下查看 TP、FP、FN、TN，并导出 FP/FN 错误样本。
        - **预测明细查询**：按标签、概率范围和商品类别筛选预测结果，并导出 CSV。

        ### 3. 数据文件

        | 文件 | 用途 |
        |---|---|
        | `data/predictions.csv` | 用户-商品预测概率、真实标签、校准后概率 |
        | `data/calibration_metrics.csv` | 概率校准整体指标 |
        | `data/calibration_bin_report.csv` | 概率分箱校准曲线 |
        | `data/top_rate_metrics.csv` | Top5%、Top10%、Top20% 指标 |
        | `data/model_comparison_from_report.csv` | 从项目报告整理的模型对比表 |
        | `data/feature_explanation_from_report.csv` | 从项目报告整理的特征业务解释 |
        """
    )
