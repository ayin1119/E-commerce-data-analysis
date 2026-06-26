-- 1. 生成小时维度表
WITH RECURSIVE hours AS (
    SELECT 0 AS purchase_hour
    UNION ALL
    SELECT purchase_hour + 1
    FROM hours
    WHERE purchase_hour < 23
),
-- 2. 按小时统计购买总次数
purchase_by_hour AS (
    SELECT
        HOUR(event_time) AS purchase_hour,
        COUNT(*) AS purchase_count
    FROM data_min
    WHERE behavior_type = 4
      AND event_time IS NOT NULL
    GROUP BY
        HOUR(event_time)
),
-- 3. 统计数据覆盖的总天数
survey_days AS (
    SELECT
        COUNT(DISTINCT DATE(event_time)) AS total_days
    FROM data_min
    WHERE event_time IS NOT NULL
),
-- 4. 计算全站总购买次数
total_purchase AS (
    SELECT
        COUNT(*) AS total_purchase_count
    FROM data_min
    WHERE behavior_type = 4
      AND event_time IS NOT NULL
),
-- 5. 关联所有数据，计算各项指标
base AS (
    SELECT
        h.purchase_hour,

        COALESCE(p.purchase_count, 0) AS purchase_count,

        sd.total_days,

        tp.total_purchase_count,

        ROUND(
            COALESCE(p.purchase_count, 0) / NULLIF(sd.total_days, 0),
            2
        ) AS avg_purchase_per_day_hour,

        ROUND(
            COALESCE(p.purchase_count, 0) / NULLIF(tp.total_purchase_count, 0),
            4
        ) AS purchase_heat,

        CONCAT(
            ROUND(
                COALESCE(p.purchase_count, 0) / NULLIF(tp.total_purchase_count, 0) * 100,
                2
            ),
            '%'
        ) AS purchase_heat_percent

    FROM hours h
    LEFT JOIN purchase_by_hour p
        ON h.purchase_hour = p.purchase_hour
    CROSS JOIN survey_days sd
    CROSS JOIN total_purchase tp
)
-- 6. 最终输出：按小时排序
SELECT
    purchase_hour,

    CONCAT(
        LPAD(purchase_hour, 2, '0'),
        ':00-',
        LPAD(purchase_hour, 2, '0'),
        ':59'
    ) AS hour_range,

    purchase_count,
    total_days,
    avg_purchase_per_day_hour,

    total_purchase_count,
    purchase_heat,
    purchase_heat_percent

FROM base
ORDER BY
    purchase_hour;