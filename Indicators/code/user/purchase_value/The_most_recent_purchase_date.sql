-- 1.取数据中的最大时间作为调查截止时间
WITH cutoff_time AS (
    SELECT 
        MAX(STR_TO_DATE(`event_time`, '%Y-%m-%d %H')) AS survey_end_time
    FROM data_min
),
-- 2.获取所有有行为的用户
all_users AS (
    SELECT DISTINCT
        user_id
    FROM data_min
),
-- 3.每个用户最后一次购买的时间
last_purchase AS (
    SELECT
        user_id,
        MAX(STR_TO_DATE(`event_time`, '%Y-%m-%d %H')) AS last_purchase_time
    FROM data_min
    WHERE behavior_type = 4
    GROUP BY user_id
)
-- 4.计算每个用户的沉默时长
SELECT
    au.user_id,
    lp.last_purchase_time,
    ct.survey_end_time,

    CASE 
        WHEN lp.last_purchase_time IS NULL THEN NULL
        ELSE TIMESTAMPDIFF(HOUR, lp.last_purchase_time, ct.survey_end_time)
    END AS hours_since_last_purchase,

    CASE 
        WHEN lp.last_purchase_time IS NULL THEN NULL
        ELSE DATEDIFF(ct.survey_end_time, lp.last_purchase_time)
    END AS days_since_last_purchase

FROM all_users au
LEFT JOIN last_purchase lp
    ON au.user_id = lp.user_id
CROSS JOIN cutoff_time ct
ORDER BY days_since_last_purchase DESC;