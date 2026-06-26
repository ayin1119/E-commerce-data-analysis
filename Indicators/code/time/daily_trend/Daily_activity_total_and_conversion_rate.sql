-- 日行为总量及转化率
SELECT
    active_date,

    total_behavior,
    total_views,
    total_fav,
    total_cart,
    total_sales,

    CONCAT(ROUND(total_fav / NULLIF(total_views, 0) * 100, 2), '%') AS view_to_fav_rate,
    CONCAT(ROUND(total_cart / NULLIF(total_fav, 0) * 100, 2), '%') AS fav_to_cart_rate,
    CONCAT(ROUND(total_sales / NULLIF(total_cart, 0) * 100, 2), '%') AS cart_to_buy_rate,
    CONCAT(ROUND(total_sales / NULLIF(total_views, 0) * 100, 2), '%') AS view_to_buy_rate

FROM (
    SELECT
        LEFT(event_time, 10) AS active_date,

        COUNT(*) AS total_behavior,

        SUM(CASE WHEN behavior_type = 1 THEN 1 ELSE 0 END) AS total_views,
        SUM(CASE WHEN behavior_type = 2 THEN 1 ELSE 0 END) AS total_fav,
        SUM(CASE WHEN behavior_type = 3 THEN 1 ELSE 0 END) AS total_cart,
        SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS total_sales

    FROM data_min
    GROUP BY
        LEFT(event_time, 10)
) t
ORDER BY
    active_date;