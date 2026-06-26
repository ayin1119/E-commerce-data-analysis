-- 1.确保所有用户都被纳入分析
WITH all_users AS (
    SELECT DISTINCT
        user_id
    FROM data_min
),
-- 2.计算每个用户在每个品类的购买次数
user_category_purchase AS (
    SELECT
        user_id,
        item_category,
        COUNT(*) AS category_purchase_count
    FROM data_min
    WHERE behavior_type = 4
    GROUP BY
        user_id,
        item_category
),
-- 3.计算每个用户的全部购买次数
user_purchase_total AS (
    SELECT
        user_id,
        SUM(category_purchase_count) AS total_purchase_count
    FROM user_category_purchase
    GROUP BY user_id
),
-- 4.对每个用户，按品类购买次数降序排名
category_rank AS (
    SELECT
        ucp.user_id,
        ucp.item_category,
        ucp.category_purchase_count,
        upt.total_purchase_count,
        ROW_NUMBER() OVER (
            PARTITION BY ucp.user_id
            ORDER BY ucp.category_purchase_count DESC, ucp.item_category
        ) AS category_rn

    FROM user_category_purchase ucp
    JOIN user_purchase_total upt
        ON ucp.user_id = upt.user_id
),
-- 5.提取每个用户的TOP1品类，计算其占总购买的比重
user_concentration AS (
    SELECT
        au.user_id,

        cr.item_category AS top_category,

        IFNULL(cr.category_purchase_count, 0) AS top_category_purchase_count,

        IFNULL(upt.total_purchase_count, 0) AS total_purchase_count,

        CASE
            WHEN IFNULL(upt.total_purchase_count, 0) = 0 THEN 0
            ELSE ROUND(cr.category_purchase_count / upt.total_purchase_count, 4)
        END AS concentration_rate

    FROM all_users au
    LEFT JOIN user_purchase_total upt
        ON au.user_id = upt.user_id
    LEFT JOIN category_rank cr
        ON au.user_id = cr.user_id
        AND cr.category_rn = 1
),
-- 6.按集中度从高到低排序，用于筛选"高集中度用户"
user_rank AS (
    SELECT
        user_id,
        top_category,
        total_purchase_count,
        concentration_rate,

        ROW_NUMBER() OVER (
            ORDER BY concentration_rate DESC, total_purchase_count DESC, user_id
        ) AS user_rn,

        COUNT(*) OVER () AS total_users

    FROM user_concentration
)
-- 6.标记前30%的用户为"集中型用户"
SELECT
    user_id,

    CASE
        WHEN total_purchase_count > 0
             AND user_rn <= CEIL(total_users * 0.3)
        THEN 1
        ELSE 0
    END AS is_concentrated,

    CASE
        WHEN total_purchase_count > 0
             AND user_rn <= CEIL(total_users * 0.3)
        THEN top_category
        ELSE NULL
    END AS concentrated_category

FROM user_rank
ORDER BY
    is_concentrated DESC,
    user_id;