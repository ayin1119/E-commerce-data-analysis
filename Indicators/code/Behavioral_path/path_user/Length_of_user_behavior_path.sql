-- 每个用户在购买前产生了多少"非购买"行为（浏览/收藏/加购）
SELECT
    user_id,

    SUM(CASE WHEN behavior_type IN (1, 2, 3) THEN 1 ELSE 0 END) AS pre_buy_behavior_count,
    SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS purchase_count,

    ROUND(
        SUM(CASE WHEN behavior_type IN (1, 2, 3) THEN 1 ELSE 0 END)
        /
        NULLIF(SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END), 0),
        4
    ) AS pre_buy_behavior_per_purchase

FROM data_min
GROUP BY user_id
HAVING purchase_count > 0
ORDER BY pre_buy_behavior_per_purchase DESC
limit 100000