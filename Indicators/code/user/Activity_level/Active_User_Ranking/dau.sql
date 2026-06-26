-- 1.计算每个用户每天的行为总次数
WITH daily_user_behavior AS (
    SELECT
        LEFT(event_time, 10) AS active_date,
        user_id,
        COUNT(*) AS num_behavior_type
    FROM data_min
    GROUP BY
        LEFT(event_time, 10),
        user_id
),
-- 2. 每日用户排名
daily_user_rank AS (
    SELECT
        active_date,
        user_id,
        num_behavior_type,
        ROW_NUMBER() OVER (
            PARTITION BY active_date
            ORDER BY num_behavior_type DESC
        ) AS user_rank
    FROM daily_user_behavior
)
-- 3. 筛选每日TOP100用户
SELECT
    active_date,
    user_id,
    num_behavior_type,
    user_rank
FROM daily_user_rank
WHERE user_rank <= 100
ORDER BY
    active_date ASC,
    user_rank ASC;