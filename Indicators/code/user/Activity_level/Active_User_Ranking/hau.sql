-- 1.计算每个用户在每个小时的行为总次数
WITH hourly_user_behavior AS (
    SELECT
        event_time,
        user_id,
        COUNT(*) AS num_behavior_type
    FROM data_min 
    GROUP BY
        event_time,
        user_id
),
-- 2.按行为次数降序排名
hourly_user_rank AS (
    SELECT
        event_time,
        user_id,
        num_behavior_type,
        ROW_NUMBER() OVER (
            PARTITION BY event_time
            ORDER BY num_behavior_type DESC
        ) AS user_rank
    FROM hourly_user_behavior
)
-- 3. 筛选每小时TOP5用户
SELECT
    event_time,
    user_id,
    num_behavior_type,
    user_rank
FROM hourly_user_rank
WHERE user_rank <= 5
ORDER BY
    event_time ASC,
    user_rank ASC;
