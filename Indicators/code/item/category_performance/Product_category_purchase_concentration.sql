-- 计算每个品类下每个商品的总购买次数
WITH item_purchase AS (
    SELECT
        item_category,
        item_id,
        COUNT(*) AS item_purchase_count
    FROM data_min
    WHERE behavior_type = 4
    GROUP BY
        item_category,
        item_id
),
-- 计算每个品类的总购买次数和包含的商品数
category_base AS (
    SELECT
        item_category,
        SUM(item_purchase_count) AS category_purchase_count,
        COUNT(*) AS category_item_count
    FROM item_purchase
    GROUP BY
        item_category
),
-- 计算每个商品在品类内的购买占比
item_share AS (
    SELECT
        ip.item_category,
        ip.item_id,
        ip.item_purchase_count,
        cb.category_purchase_count,
        cb.category_item_count,

        ip.item_purchase_count / NULLIF(cb.category_purchase_count, 0) AS item_purchase_share,

        ROW_NUMBER() OVER (
            PARTITION BY ip.item_category
            ORDER BY ip.item_purchase_count DESC, ip.item_id
        ) AS item_rank

    FROM item_purchase ip
    JOIN category_base cb
        ON ip.item_category = cb.item_category
),
-- 计算TOP1/TOP5占比、HHI指数
category_concentration AS (
    SELECT
        item_category,

        MAX(category_purchase_count) AS category_purchase_count,
        MAX(category_item_count) AS category_item_count,

        MAX(CASE WHEN item_rank = 1 THEN item_id END) AS top1_item_id,
        MAX(CASE WHEN item_rank = 1 THEN item_purchase_count END) AS top1_purchase_count,
        ROUND(MAX(CASE WHEN item_rank = 1 THEN item_purchase_share END), 4) AS top1_purchase_share,

        SUM(CASE WHEN item_rank <= 5 THEN item_purchase_count ELSE 0 END) AS top5_purchase_count,

        ROUND(
            SUM(CASE WHEN item_rank <= 5 THEN item_purchase_count ELSE 0 END)
            / NULLIF(MAX(category_purchase_count), 0),
            4
        ) AS top5_purchase_share,

        ROUND(SUM(POWER(item_purchase_share, 2)), 4) AS category_hhi,

        ROUND(
            CASE
                WHEN MAX(category_item_count) = 1 THEN 1
                ELSE
                    (
                        SUM(POWER(item_purchase_share, 2)) - 1 / MAX(category_item_count)
                    )
                    /
                    (
                        1 - 1 / MAX(category_item_count)
                    )
            END,
            4
        ) AS normalized_category_hhi

    FROM item_share
    GROUP BY
        item_category
)
-- 定义集中度类型标签
SELECT
    item_category,
    category_purchase_count,
    category_item_count,

    top1_item_id,
    top1_purchase_count,
    top1_purchase_share,

    top5_purchase_count,
    top5_purchase_share,

    category_hhi,
    normalized_category_hhi,

    CASE
        WHEN normalized_category_hhi >= 0.5 THEN '高集中品类'
        WHEN normalized_category_hhi >= 0.2 THEN '中集中品类'
        ELSE '分散型品类'
    END AS category_concentration_type

FROM category_concentration
ORDER BY
    normalized_category_hhi DESC,
    category_purchase_count DESC
limit 9000