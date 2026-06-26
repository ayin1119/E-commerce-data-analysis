CREATE INDEX idx_data_user_item_time_behavior
ON data_min(user_id, item_id, event_time, behavior_type);
DROP TABLE IF EXISTS ml_user_item_feature_7d_all;

CREATE TABLE ml_user_item_feature_7d_all (
    dataset_type VARCHAR(20),
    snapshot_date DATE,
    user_id BIGINT,
    item_id BIGINT,

    user_item_total_behavior_count_7d INT,
    user_item_view_count_7d INT,
    user_item_fav_count_7d INT,
    user_item_cart_count_7d INT,
    user_item_purchase_count_7d INT,

    user_item_active_days_7d INT,

    user_item_last_behavior_days INT,
    user_item_last_view_days INT,
    user_item_last_fav_days INT,
    user_item_last_cart_days INT,
    user_item_last_purchase_days INT,

    user_item_has_view INT,
    user_item_has_fav INT,
    user_item_has_cart INT,
    user_item_has_purchase INT,

    user_item_cart_rate_7d DECIMAL(10,4),
    user_item_purchase_rate_7d DECIMAL(10,4)
);
INSERT INTO ml_user_item_feature_7d_all
SELECT
    'train' AS dataset_type,
    '2014-11-24' AS snapshot_date,
    s.user_id,
    s.item_id,

    COUNT(d.behavior_type) AS user_item_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_item_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_item_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_item_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_item_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_item_active_days_7d,

    COALESCE(DATEDIFF('2014-11-24', MAX(LEFT(d.event_time, 10))), 999) AS user_item_last_behavior_days,

    COALESCE(DATEDIFF(
        '2014-11-24',
        MAX(CASE WHEN d.behavior_type = 1 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_view_days,

    COALESCE(DATEDIFF(
        '2014-11-24',
        MAX(CASE WHEN d.behavior_type = 2 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_fav_days,

    COALESCE(DATEDIFF(
        '2014-11-24',
        MAX(CASE WHEN d.behavior_type = 3 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_cart_days,

    COALESCE(DATEDIFF(
        '2014-11-24',
        MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_purchase_days,

    MAX(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_item_has_view,
    MAX(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_item_has_fav,
    MAX(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_item_has_cart,
    MAX(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_item_has_purchase,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_item_cart_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_item_purchase_rate_7d

FROM ml_label_buy_7d_sampled s
JOIN data_min d
    ON s.user_id = d.user_id
   AND s.item_id = d.item_id
   AND d.event_time >= '2014-11-18'
   AND d.event_time <  '2014-11-25'
WHERE s.dataset_type = 'train'
GROUP BY
    s.user_id,
    s.item_id;
INSERT INTO ml_user_item_feature_7d_all
SELECT
    'valid' AS dataset_type,
    '2014-12-01' AS snapshot_date,
    s.user_id,
    s.item_id,

    COUNT(d.behavior_type) AS user_item_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_item_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_item_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_item_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_item_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_item_active_days_7d,

    COALESCE(DATEDIFF('2014-12-01', MAX(LEFT(d.event_time, 10))), 999) AS user_item_last_behavior_days,

    COALESCE(DATEDIFF(
        '2014-12-01',
        MAX(CASE WHEN d.behavior_type = 1 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_view_days,

    COALESCE(DATEDIFF(
        '2014-12-01',
        MAX(CASE WHEN d.behavior_type = 2 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_fav_days,

    COALESCE(DATEDIFF(
        '2014-12-01',
        MAX(CASE WHEN d.behavior_type = 3 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_cart_days,

    COALESCE(DATEDIFF(
        '2014-12-01',
        MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_purchase_days,

    MAX(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_item_has_view,
    MAX(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_item_has_fav,
    MAX(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_item_has_cart,
    MAX(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_item_has_purchase,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_item_cart_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_item_purchase_rate_7d

FROM ml_label_buy_7d_sampled s
JOIN data_min d
    ON s.user_id = d.user_id
   AND s.item_id = d.item_id
   AND d.event_time >= '2014-11-25'
   AND d.event_time <  '2014-12-02'
WHERE s.dataset_type = 'valid'
GROUP BY
    s.user_id,
    s.item_id;
INSERT INTO ml_user_item_feature_7d_all
SELECT
    'test' AS dataset_type,
    '2014-12-11' AS snapshot_date,
    s.user_id,
    s.item_id,

    COUNT(d.behavior_type) AS user_item_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_item_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_item_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_item_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_item_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_item_active_days_7d,

    COALESCE(DATEDIFF('2014-12-11', MAX(LEFT(d.event_time, 10))), 999) AS user_item_last_behavior_days,

    COALESCE(DATEDIFF(
        '2014-12-11',
        MAX(CASE WHEN d.behavior_type = 1 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_view_days,

    COALESCE(DATEDIFF(
        '2014-12-11',
        MAX(CASE WHEN d.behavior_type = 2 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_fav_days,

    COALESCE(DATEDIFF(
        '2014-12-11',
        MAX(CASE WHEN d.behavior_type = 3 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_cart_days,

    COALESCE(DATEDIFF(
        '2014-12-11',
        MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
    ), 999) AS user_item_last_purchase_days,

    MAX(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_item_has_view,
    MAX(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_item_has_fav,
    MAX(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_item_has_cart,
    MAX(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_item_has_purchase,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_item_cart_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_item_purchase_rate_7d

FROM ml_label_buy_7d_sampled s
JOIN data_min d
    ON s.user_id = d.user_id
   AND s.item_id = d.item_id
   AND d.event_time >= '2014-12-05'
   AND d.event_time <  '2014-12-12'
WHERE s.dataset_type = 'test'
GROUP BY
    s.user_id,
    s.item_id;
CREATE INDEX idx_ui_feature_user_item
ON ml_user_item_feature_7d_all(dataset_type, snapshot_date, user_id, item_id);
SELECT
    dataset_type,
    COUNT(*) AS feature_rows
FROM ml_user_item_feature_7d_all
GROUP BY
    dataset_type;