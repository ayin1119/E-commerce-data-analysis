-- 1.统计每天各行为类型的总次数
WITH daily_behavior_counts AS (
    SELECT
        DATE(event_time) AS event_date,
        COUNT(*) AS total_behavior_count,
        SUM(CASE WHEN behavior_type = 1 THEN 1 ELSE 0 END) AS browse_count,
        SUM(CASE WHEN behavior_type = 2 THEN 1 ELSE 0 END) AS favorite_count,
        SUM(CASE WHEN behavior_type = 3 THEN 1 ELSE 0 END) AS cart_count,
        SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS purchase_count
    FROM data_min
    WHERE event_time IS NOT NULL
    GROUP BY DATE(event_time)
)
-- 2. 计算每日各环节转化率
SELECT
    event_date,
    total_behavior_count,
    browse_count,
    favorite_count,
    cart_count,
    purchase_count,

    ROUND(favorite_count / NULLIF(browse_count, 0), 4) AS browse_to_favorite_rate,
    ROUND(cart_count / NULLIF(favorite_count, 0), 4) AS favorite_to_cart_rate,
    ROUND(purchase_count / NULLIF(cart_count, 0), 4) AS cart_to_purchase_rate,
    ROUND(purchase_count / NULLIF(browse_count, 0), 4) AS browse_to_purchase_rate
FROM daily_behavior_counts
ORDER BY event_date;