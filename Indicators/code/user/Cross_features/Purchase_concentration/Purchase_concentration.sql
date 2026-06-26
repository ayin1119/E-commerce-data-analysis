-- 基于购买次数和商品多样性，将用户分为不同类型
SELECT
    user_id,
    total_purchase_count,
    distinct_purchase_item_count,
    purchase_concentration,

    CASE
        WHEN total_purchase_count < 3
        THEN '低购买用户'

        WHEN purchase_concentration >= 2
         AND distinct_purchase_item_count <= total_purchase_count / 2
        THEN '少量多次型用户'

        WHEN purchase_concentration < 2
         AND distinct_purchase_item_count >= 3
        THEN '多商品少次型用户'

        WHEN total_purchase_count >= 10
         AND distinct_purchase_item_count >= 5
        THEN '广泛多次型用户'

        ELSE '一般购买用户'
    END AS purchase_concentration_type

FROM (
	-- 按用户聚合购买数据
    SELECT
        user_id,

        COUNT(*) AS total_purchase_count,

        COUNT(DISTINCT item_id) AS distinct_purchase_item_count,

        ROUND(
            COUNT(*) / NULLIF(COUNT(DISTINCT item_id), 0),
            4
        ) AS purchase_concentration

    FROM data_min
    WHERE behavior_type = 4
    GROUP BY user_id
) t
ORDER BY
    purchase_concentration DESC,
    total_purchase_count DESC
LIMIT 100000;