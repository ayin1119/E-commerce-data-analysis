-- 计算商品转化率
SELECT
	item_category,
    item_id,

    total_views,
    total_fav,
    total_cart,
    total_sales,

    ROUND(total_fav / NULLIF(total_views, 0), 4) AS view_to_fav_rate,
    ROUND(total_cart / NULLIF(total_fav, 0), 4) AS fav_to_cart_rate,
    ROUND(total_sales / NULLIF(total_cart, 0), 4) AS cart_to_buy_rate,
    ROUND(total_sales / NULLIF(total_views, 0), 4) AS view_to_buy_rate

FROM item_behavior_summary
ORDER BY
    item_category,view_to_buy_rate DESC
limit 3000000