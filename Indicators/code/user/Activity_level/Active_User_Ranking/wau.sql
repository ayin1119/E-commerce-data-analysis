-- 1.计算每条记录所属的周起始日期
WITH base AS (
    SELECT
        user_id,
        behavior_type,
        event_time,
        DATE_SUB(DATE(event_time), INTERVAL WEEKDAY(event_time) DAY) AS week_start_date
    FROM data_min
    WHERE event_time IS NOT NULL
),
-- 2.计算每个用户每周的行为总次数
weekly_user_behavior AS (
    SELECT
        week_start_date,
        DATE_ADD(week_start_date, INTERVAL 6 DAY) AS week_end_date,
        user_id,
        COUNT(*) AS overall_activity
    FROM base
    GROUP BY
        week_start_date,
        user_id
),
-- 3.按行为次数降序排名
weekly_user_rank AS (
    SELECT
        week_start_date,
        week_end_date,
        user_id,
        overall_activity,
        ROW_NUMBER() OVER (
            PARTITION BY week_start_date
            ORDER BY overall_activity DESC
        ) AS user_rank
    FROM weekly_user_behavior
)
-- 4. 筛选每周TOP1000用户
SELECT
    week_start_date,
    week_end_date,
    user_id,
    overall_activity,
    user_rank
FROM weekly_user_rank
WHERE user_rank <= 1000
ORDER BY
    week_start_date ASC,
    user_rank ASC;