DROP TABLE IF EXISTS ml_feature_wide_table_v1;

CREATE TABLE ml_feature_wide_table_v1 AS
SELECT
    l.dataset_type,
    l.snapshot_date,
    l.user_id,
    l.item_id,
    l.item_category,
    l.label_buy_7d,

    COALESCE(ui.user_item_total_behavior_count_7d, 0) AS user_item_total_behavior_count_7d,
    COALESCE(ui.user_item_view_count_7d, 0) AS user_item_view_count_7d,
    COALESCE(ui.user_item_fav_count_7d, 0) AS user_item_fav_count_7d,
    COALESCE(ui.user_item_cart_count_7d, 0) AS user_item_cart_count_7d,
    COALESCE(ui.user_item_purchase_count_7d, 0) AS user_item_purchase_count_7d,

    COALESCE(ui.user_item_active_days_7d, 0) AS user_item_active_days_7d,

    COALESCE(ui.user_item_last_behavior_days, 999) AS user_item_last_behavior_days,
    COALESCE(ui.user_item_last_view_days, 999) AS user_item_last_view_days,
    COALESCE(ui.user_item_last_fav_days, 999) AS user_item_last_fav_days,
    COALESCE(ui.user_item_last_cart_days, 999) AS user_item_last_cart_days,
    COALESCE(ui.user_item_last_purchase_days, 999) AS user_item_last_purchase_days,

    COALESCE(ui.user_item_has_view, 0) AS user_item_has_view,
    COALESCE(ui.user_item_has_fav, 0) AS user_item_has_fav,
    COALESCE(ui.user_item_has_cart, 0) AS user_item_has_cart,
    COALESCE(ui.user_item_has_purchase, 0) AS user_item_has_purchase,

    COALESCE(ui.user_item_cart_rate_7d, 0) AS user_item_cart_rate_7d,
    COALESCE(ui.user_item_purchase_rate_7d, 0) AS user_item_purchase_rate_7d,

    COALESCE(u.user_total_behavior_count_7d, 0) AS user_total_behavior_count_7d,
    COALESCE(u.user_view_count_7d, 0) AS user_view_count_7d,
    COALESCE(u.user_fav_count_7d, 0) AS user_fav_count_7d,
    COALESCE(u.user_cart_count_7d, 0) AS user_cart_count_7d,
    COALESCE(u.user_purchase_count_7d, 0) AS user_purchase_count_7d,

    COALESCE(u.user_active_days_7d, 0) AS user_active_days_7d,
    COALESCE(u.user_behavior_item_count_7d, 0) AS user_behavior_item_count_7d,
    COALESCE(u.user_behavior_category_count_7d, 0) AS user_behavior_category_count_7d,

    COALESCE(u.user_purchase_item_count_7d, 0) AS user_purchase_item_count_7d,
    COALESCE(u.user_purchase_category_count_7d, 0) AS user_purchase_category_count_7d,

    COALESCE(u.user_purchase_rate_7d, 0) AS user_purchase_rate_7d,
    COALESCE(u.user_cart_rate_7d, 0) AS user_cart_rate_7d,

    COALESCE(u.user_last_behavior_days, 999) AS user_last_behavior_days,
    COALESCE(u.user_last_purchase_days, 999) AS user_last_purchase_days,

    COALESCE(i.item_total_behavior_count_7d, 0) AS item_total_behavior_count_7d,
    COALESCE(i.item_view_count_7d, 0) AS item_view_count_7d,
    COALESCE(i.item_fav_count_7d, 0) AS item_fav_count_7d,
    COALESCE(i.item_cart_count_7d, 0) AS item_cart_count_7d,
    COALESCE(i.item_purchase_count_7d, 0) AS item_purchase_count_7d,

    COALESCE(i.item_behavior_user_count_7d, 0) AS item_behavior_user_count_7d,
    COALESCE(i.item_purchase_user_count_7d, 0) AS item_purchase_user_count_7d,
    COALESCE(i.item_active_days_7d, 0) AS item_active_days_7d,

    COALESCE(i.item_view_to_fav_rate_7d, 0) AS item_view_to_fav_rate_7d,
    COALESCE(i.item_fav_to_cart_rate_7d, 0) AS item_fav_to_cart_rate_7d,
    COALESCE(i.item_cart_to_buy_rate_7d, 0) AS item_cart_to_buy_rate_7d,
    COALESCE(i.item_view_to_buy_rate_7d, 0) AS item_view_to_buy_rate_7d,

    COALESCE(i.item_last_behavior_days, 999) AS item_last_behavior_days,
    COALESCE(i.item_last_purchase_days, 999) AS item_last_purchase_days,

    COALESCE(uc.user_category_total_behavior_count_7d, 0) AS user_category_total_behavior_count_7d,
    COALESCE(uc.user_category_view_count_7d, 0) AS user_category_view_count_7d,
    COALESCE(uc.user_category_fav_count_7d, 0) AS user_category_fav_count_7d,
    COALESCE(uc.user_category_cart_count_7d, 0) AS user_category_cart_count_7d,
    COALESCE(uc.user_category_purchase_count_7d, 0) AS user_category_purchase_count_7d,

    COALESCE(uc.user_category_active_days_7d, 0) AS user_category_active_days_7d,
    COALESCE(uc.user_category_behavior_item_count_7d, 0) AS user_category_behavior_item_count_7d,
    COALESCE(uc.user_category_purchase_item_count_7d, 0) AS user_category_purchase_item_count_7d,

    COALESCE(uc.user_category_purchase_rate_7d, 0) AS user_category_purchase_rate_7d,
    COALESCE(uc.user_category_cart_rate_7d, 0) AS user_category_cart_rate_7d,

    COALESCE(uc.user_category_behavior_share_7d, 0) AS user_category_behavior_share_7d,
    COALESCE(uc.user_category_purchase_share_7d, 0) AS user_category_purchase_share_7d,

    COALESCE(uc.user_category_last_behavior_days, 999) AS user_category_last_behavior_days,
    COALESCE(uc.user_category_last_purchase_days, 999) AS user_category_last_purchase_days

FROM ml_label_buy_7d_sampled l

LEFT JOIN ml_user_item_feature_7d_all ui
    ON l.dataset_type = ui.dataset_type
   AND l.snapshot_date = ui.snapshot_date
   AND l.user_id = ui.user_id
   AND l.item_id = ui.item_id

LEFT JOIN ml_user_feature_7d_all u
    ON l.dataset_type = u.dataset_type
   AND l.snapshot_date = u.snapshot_date
   AND l.user_id = u.user_id

LEFT JOIN ml_item_feature_7d_all i
    ON l.dataset_type = i.dataset_type
   AND l.snapshot_date = i.snapshot_date
   AND l.item_id = i.item_id
   AND l.item_category = i.item_category

LEFT JOIN ml_user_category_feature_7d_all uc
    ON l.dataset_type = uc.dataset_type
   AND l.snapshot_date = uc.snapshot_date
   AND l.user_id = uc.user_id
   AND l.item_category = uc.item_category;
CREATE INDEX idx_wide_dataset_label
ON ml_feature_wide_table_v1(dataset_type, label_buy_7d);

CREATE INDEX idx_wide_user_item
ON ml_feature_wide_table_v1(dataset_type, snapshot_date, user_id, item_id);
SELECT
    dataset_type,
    COUNT(*) AS wide_table_rows
FROM ml_feature_wide_table_v1
GROUP BY
    dataset_type
ORDER BY
    dataset_type;
SELECT
    dataset_type,
    label_buy_7d,
    COUNT(*) AS sample_count,
    ROUND(
        COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY dataset_type),
        4
    ) AS sample_ratio,
    CONCAT(
        ROUND(
            COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY dataset_type) * 100,
            2
        ),
        '%'
    ) AS sample_ratio_percent
FROM ml_feature_wide_table_v1
GROUP BY
    dataset_type,
    label_buy_7d
ORDER BY
    dataset_type,
    label_buy_7d;
SELECT
    dataset_type,
    snapshot_date,
    user_id,
    item_id,
    COUNT(*) AS duplicate_count
FROM ml_feature_wide_table_v1
GROUP BY
    dataset_type,
    snapshot_date,
    user_id,
    item_id
HAVING COUNT(*) > 1;
SELECT *
FROM ml_feature_wide_table_v1
LIMIT 100;