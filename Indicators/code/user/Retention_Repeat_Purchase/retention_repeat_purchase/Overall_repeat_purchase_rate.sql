-- 整体复购率
SELECT
    COUNT(*) AS total_users,
    SUM(CASE WHEN purchase_count >= 2 THEN 1 ELSE 0 END) AS repurchase_users,
    ROUND(SUM(CASE WHEN purchase_count >= 2 THEN 1 ELSE 0 END) / COUNT(*), 4) AS repurchase_rate
FROM (
    SELECT
        user_id,
        COUNT(CASE WHEN behavior_type = 4 THEN 1 END) AS purchase_count
    FROM data_min
    GROUP BY user_id
) t;