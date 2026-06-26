-- 1. 计算用户购买品类
WITH user_purchase_category AS (
    SELECT
        user_id,
        COUNT(DISTINCT item_category) AS distinct_purchase_category_count,
        COUNT(*) AS total_purchase_count
    FROM data_min
    WHERE behavior_type = 4
    GROUP BY user_id
),
-- 2. 定义用户类型
user_category_type AS (
    SELECT
        user_id,
        distinct_purchase_category_count,
        total_purchase_count,
        CASE
            WHEN distinct_purchase_category_count >= 2 THEN '跨品类购买用户'
            ELSE '单品类购买用户'
        END AS purchase_category_type
    FROM user_purchase_category
)
-- 3. 计算各类用户数量及占比
SELECT
    COUNT(*) AS total_purchase_users,

    SUM(CASE 
            WHEN purchase_category_type = '单品类购买用户' 
            THEN 1 ELSE 0 
        END) AS single_category_purchase_users,

    SUM(CASE 
            WHEN purchase_category_type = '跨品类购买用户' 
            THEN 1 ELSE 0 
        END) AS cross_category_purchase_users,

    ROUND(
        SUM(CASE 
                WHEN purchase_category_type = '跨品类购买用户' 
                THEN 1 ELSE 0 
            END) / COUNT(*),
        4
    ) AS cross_category_purchase_user_ratio,

    CONCAT(
        ROUND(
            SUM(CASE 
                    WHEN purchase_category_type = '跨品类购买用户' 
                    THEN 1 ELSE 0 
                END) / COUNT(*) * 100,
            2
        ),
        '%'
    ) AS cross_category_purchase_user_ratio_percent

FROM user_category_type;