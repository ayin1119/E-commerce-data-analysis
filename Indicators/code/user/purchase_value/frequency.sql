-- 1.计算数据覆盖的总天数
WITH survey_period AS (
    SELECT
        MIN(DATE(event_time)) AS survey_start_date,
        MAX(DATE(event_time)) AS survey_end_date,
        DATEDIFF(
            MAX(DATE(event_time)),
            MIN(DATE(event_time))
        ) + 1 AS survey_days
    FROM data_min
    WHERE event_time IS NOT NULL
),
-- 2.获取所有有行为的用户
all_users AS (
    SELECT DISTINCT
        user_id
    FROM data_min
    WHERE event_time IS NOT NULL
),
-- 3.每个用户有多少天产生了购买
user_purchase_days AS (
    SELECT
        user_id,
        COUNT(DISTINCT DATE(event_time)) AS purchase_days,
        COUNT(*) AS purchase_count
    FROM data_min
    WHERE behavior_type = 4
      AND event_time IS NOT NULL
    GROUP BY user_id
)
-- 4.计算每个用户的购买频率指标
SELECT
    au.user_id,
    IFNULL(upd.purchase_days, 0) AS purchase_days,
    IFNULL(upd.purchase_count, 0) AS purchase_count,

    CASE
        WHEN IFNULL(upd.purchase_days, 0) = 0 THEN NULL
        ELSE ROUND(sp.survey_days / upd.purchase_days, 2)
    END AS avg_days_per_purchase_day,

    ROUND(IFNULL(upd.purchase_days, 0) / sp.survey_days, 4) AS purchase_day_frequency

FROM all_users au
LEFT JOIN user_purchase_days upd
    ON au.user_id = upd.user_id
CROSS JOIN survey_period sp
ORDER BY
    avg_days_per_purchase_day DESC;