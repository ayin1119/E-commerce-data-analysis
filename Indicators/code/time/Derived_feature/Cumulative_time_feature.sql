-- 1. 按日期统计四种行为的每日总量
WITH daily_behavior AS (
    SELECT
        LEFT(event_time, 10) AS active_date,

        COUNT(*) AS daily_total_behavior,

        SUM(CASE WHEN behavior_type = 1 THEN 1 ELSE 0 END) AS daily_views,
        SUM(CASE WHEN behavior_type = 2 THEN 1 ELSE 0 END) AS daily_fav,
        SUM(CASE WHEN behavior_type = 3 THEN 1 ELSE 0 END) AS daily_cart,
        SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS daily_purchase_count

    FROM data_min
    GROUP BY
        LEFT(event_time, 10)
),
-- 2. 计算从第一天到当前日期的累积值
base AS (
    SELECT
        active_date,

        DATEDIFF(
            active_date,
            MIN(active_date) OVER ()
        ) + 1 AS day_index,

        daily_total_behavior,
        daily_views,
        daily_fav,
        daily_cart,
        daily_purchase_count,

        SUM(daily_total_behavior) OVER (
            ORDER BY active_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_total_behavior,

        SUM(daily_views) OVER (
            ORDER BY active_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_views,

        SUM(daily_fav) OVER (
            ORDER BY active_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_fav,

        SUM(daily_cart) OVER (
            ORDER BY active_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_cart,

        SUM(daily_purchase_count) OVER (
            ORDER BY active_date
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_purchase

    FROM daily_behavior
)
-- 3. 每日数据 + 累积数据 + 累积转化率
SELECT
    active_date,
    day_index,

    daily_total_behavior,
    daily_views,
    daily_fav,
    daily_cart,
    daily_purchase_count,

    cumulative_total_behavior,
    cumulative_views,
    cumulative_fav,
    cumulative_cart,
    cumulative_purchase,

    ROUND(
        cumulative_purchase / NULLIF(cumulative_total_behavior, 0),
        4
    ) AS cumulative_purchase_rate,

    CONCAT(
        ROUND(
            cumulative_purchase / NULLIF(cumulative_total_behavior, 0) * 100,
            2
        ),
        '%'
    ) AS cumulative_purchase_rate_percent,

    ROUND(
        cumulative_purchase / NULLIF(cumulative_views, 0),
        4
    ) AS cumulative_view_to_buy_rate,

    CONCAT(
        ROUND(
            cumulative_purchase / NULLIF(cumulative_views, 0) * 100,
            2
        ),
        '%'
    ) AS cumulative_view_to_buy_rate_percent

FROM base
ORDER BY
    active_date;