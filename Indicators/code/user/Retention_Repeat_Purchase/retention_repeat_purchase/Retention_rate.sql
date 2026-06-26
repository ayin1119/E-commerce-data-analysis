-- 1. 获取所有用户的有效活跃日期
WITH active_days AS (
    SELECT DISTINCT
        user_id,
        DATE(event_time) AS active_date
    FROM data_min
    WHERE behavior_type IN (1, 2, 3, 4)
      AND event_time IS NOT NULL
),
-- 2.获取活跃数据中的最大日期
survey_range AS (
    SELECT
        MAX(active_date) AS max_date
    FROM active_days
),
-- 3.以每个用户的第一天为基准，标记未来各日期的留存状态
retention_base AS (
    SELECT
        a0.active_date AS cohort_date,
        a0.user_id,

        MAX(CASE
            WHEN a1.active_date = DATE_ADD(a0.active_date, INTERVAL 1 DAY)
            THEN 1 ELSE 0
        END) AS retained_1d,

        MAX(CASE
            WHEN a1.active_date = DATE_ADD(a0.active_date, INTERVAL 3 DAY)
            THEN 1 ELSE 0
        END) AS retained_3d,

        MAX(CASE
            WHEN a1.active_date = DATE_ADD(a0.active_date, INTERVAL 7 DAY)
            THEN 1 ELSE 0
        END) AS retained_7d

    FROM active_days a0
    LEFT JOIN active_days a1
        ON a0.user_id = a1.user_id
       AND a1.active_date IN (
            DATE_ADD(a0.active_date, INTERVAL 1 DAY),
            DATE_ADD(a0.active_date, INTERVAL 3 DAY),
            DATE_ADD(a0.active_date, INTERVAL 7 DAY)
       )
    GROUP BY
        a0.active_date,
        a0.user_id
)
-- 4. 按基准日聚合，计算留存率
SELECT
    rb.cohort_date,

    COUNT(*) AS active_users,

    SUM(rb.retained_1d) AS retained_1d_users,
    ROUND(SUM(rb.retained_1d) / COUNT(*), 4) AS retention_1d_rate,

    SUM(rb.retained_3d) AS retained_3d_users,
    ROUND(SUM(rb.retained_3d) / COUNT(*), 4) AS retention_3d_rate,

    SUM(rb.retained_7d) AS retained_7d_users,
    ROUND(SUM(rb.retained_7d) / COUNT(*), 4) AS retention_7d_rate

FROM retention_base rb
CROSS JOIN survey_range sr
WHERE DATE_ADD(rb.cohort_date, INTERVAL 7 DAY) <= sr.max_date
GROUP BY
    rb.cohort_date
ORDER BY
    rb.cohort_date;