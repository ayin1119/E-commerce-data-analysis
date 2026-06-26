-- 统计所有用户在购买前产生的"非购买"行为总量
SELECT
    SUM(CASE WHEN behavior_type IN (1, 2, 3) THEN 1 ELSE 0 END) AS pre_buy_behavior_count,
    SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS purchase_count,

    ROUND(
        SUM(CASE WHEN behavior_type IN (1, 2, 3) THEN 1 ELSE 0 END)
        /
        NULLIF(SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END), 0),
        4
    ) AS pre_buy_behavior_per_purchase
FROM data_min;