-- 统计每个用户的整体行为量、购买量、购买商品多样性及购买转化率
SELECT
    user_id,

    COUNT(*) AS total_behavior_count,

    SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS total_purchase_count,

    COUNT(DISTINCT CASE 
        WHEN behavior_type = 4 THEN item_id 
    END) AS distinct_purchase_item_count,

    ROUND(
        SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) 
        / NULLIF(COUNT(*), 0),
        4
    ) AS purchase_rate

FROM data_min
WHERE event_time IS NOT NULL
GROUP BY user_id
ORDER BY total_purchase_count DESC, purchase_rate DESC;