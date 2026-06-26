-- 计算每个商品在其所属品类中的购买占比
SELECT
    item_category,
    item_id,
    item_purchase_count,
    category_purchase_count,

    CONCAT(
        ROUND(
            item_purchase_count / NULLIF(category_purchase_count, 0) * 100,
            2
        ),
        '%'
    ) AS item_purchase_share

FROM (
    SELECT
        item_category,
        item_id,
        COUNT(*) AS item_purchase_count,
        SUM(COUNT(*)) OVER (PARTITION BY item_category) AS category_purchase_count
    FROM data_min
    WHERE behavior_type = 4
    GROUP BY
        item_category,
        item_id
) t

ORDER BY
    item_category,
    item_purchase_count / NULLIF(category_purchase_count, 0) DESC,
    item_purchase_count DESC;