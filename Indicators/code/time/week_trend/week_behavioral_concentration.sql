-- 1. 生成星期几维度表：0=周一，1=周二，...，6=周日
WITH RECURSIVE weekdays AS (
    SELECT 0 AS weekday_num
    UNION ALL
    SELECT weekday_num + 1
    FROM weekdays
    WHERE weekday_num < 6
),
-- 2. 按星期几统计购买总次数
purchase_by_weekday AS (
    SELECT
        WEEKDAY(event_time) AS weekday_num,
        COUNT(*) AS purchase_count
    FROM data_min
    WHERE behavior_type = 4
      AND event_time IS NOT NULL
    GROUP BY
        WEEKDAY(event_time)
),
-- 3. 统计每个星期几在数据中出现的天数
weekday_days AS (
    SELECT
        WEEKDAY(event_date) AS weekday_num,
        COUNT(*) AS weekday_days
    FROM (
        SELECT DISTINCT
            DATE(event_time) AS event_date
        FROM data_min
        WHERE event_time IS NOT NULL
    ) d
    GROUP BY
        WEEKDAY(event_date)
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
        w.weekday_num,

        CASE w.weekday_num
            WHEN 0 THEN '星期一'
            WHEN 1 THEN '星期二'
            WHEN 2 THEN '星期三'
            WHEN 3 THEN '星期四'
            WHEN 4 THEN '星期五'
            WHEN 5 THEN '星期六'
            WHEN 6 THEN '星期日'
        END AS weekday_name,

        COALESCE(p.purchase_count, 0) AS purchase_count,

        COALESCE(d.weekday_days, 0) AS weekday_days,

        ROUND(
            COALESCE(p.purchase_count, 0) / NULLIF(d.weekday_days, 0),
            2
        ) AS avg_purchase_per_weekday,

        tp.total_purchase_count,

        ROUND(
            COALESCE(p.purchase_count, 0) / NULLIF(tp.total_purchase_count, 0),
            4
        ) AS purchase_concentration,

        CONCAT(
            ROUND(
                COALESCE(p.purchase_count, 0) / NULLIF(tp.total_purchase_count, 0) * 100,
                2
            ),
            '%'
        ) AS purchase_concentration_percent

    FROM weekdays w
    LEFT JOIN purchase_by_weekday p
        ON w.weekday_num = p.weekday_num
    LEFT JOIN weekday_days d
        ON w.weekday_num = d.weekday_num
    CROSS JOIN total_purchase tp
)
-- 6. 最终输出：按星期几排序（周一→周日）
SELECT
    weekday_num,
    weekday_name,

    purchase_count,
    weekday_days,
    avg_purchase_per_weekday,

    total_purchase_count,
    purchase_concentration,
    purchase_concentration_percent

FROM base
ORDER BY
    weekday_num;