DROP TABLE IF EXISTS ml_sampled_items_all;

CREATE TABLE ml_sampled_items_all AS
SELECT DISTINCT
    dataset_type,
    snapshot_date,
    item_id,
    item_category
FROM ml_label_buy_7d_sampled;
CREATE INDEX idx_sampled_items
ON ml_sampled_items_all(dataset_type, snapshot_date, item_id, item_category);
CREATE INDEX idx_data_item_time_behavior
ON data_min(item_id, item_category, event_time, behavior_type, user_id);
DROP TABLE IF EXISTS ml_item_feature_7d_all;

CREATE TABLE ml_item_feature_7d_all (
    dataset_type VARCHAR(20),
    snapshot_date DATE,
    item_id BIGINT,
    item_category BIGINT,

    item_total_behavior_count_7d INT,
    item_view_count_7d INT,
    item_fav_count_7d INT,
    item_cart_count_7d INT,
    item_purchase_count_7d INT,

    item_behavior_user_count_7d INT,
    item_purchase_user_count_7d INT,
    item_active_days_7d INT,

    item_view_to_fav_rate_7d DECIMAL(10,4),
    item_fav_to_cart_rate_7d DECIMAL(10,4),
    item_cart_to_buy_rate_7d DECIMAL(10,4),
    item_view_to_buy_rate_7d DECIMAL(10,4),

    item_last_behavior_days INT,
    item_last_purchase_days INT
);
INSERT INTO ml_item_feature_7d_all
SELECT
    'train' AS dataset_type,
    '2014-11-24' AS snapshot_date,
    s.item_id,
    s.item_category,

    COUNT(d.behavior_type) AS item_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS item_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS item_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS item_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS item_purchase_count_7d,

    COUNT(DISTINCT d.user_id) AS item_behavior_user_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.user_id END) AS item_purchase_user_count_7d,
    COUNT(DISTINCT LEFT(d.event_time, 10)) AS item_active_days_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_view_to_fav_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_fav_to_cart_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_cart_to_buy_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_view_to_buy_rate_7d,

    COALESCE(
        DATEDIFF('2014-11-24', MAX(LEFT(d.event_time, 10))),
        999
    ) AS item_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-11-24',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS item_last_purchase_days

FROM ml_sampled_items_all s

LEFT JOIN data_min d
    ON s.item_id = d.item_id
   AND s.item_category = d.item_category
   AND d.event_time >= '2014-11-18'
   AND d.event_time <  '2014-11-25'

WHERE s.dataset_type = 'train'

GROUP BY
    s.item_id,
    s.item_category;
INSERT INTO ml_item_feature_7d_all
SELECT
    'valid' AS dataset_type,
    '2014-12-01' AS snapshot_date,
    s.item_id,
    s.item_category,

    COUNT(d.behavior_type) AS item_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS item_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS item_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS item_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS item_purchase_count_7d,

    COUNT(DISTINCT d.user_id) AS item_behavior_user_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.user_id END) AS item_purchase_user_count_7d,
    COUNT(DISTINCT LEFT(d.event_time, 10)) AS item_active_days_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_view_to_fav_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_fav_to_cart_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_cart_to_buy_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_view_to_buy_rate_7d,

    COALESCE(
        DATEDIFF('2014-12-01', MAX(LEFT(d.event_time, 10))),
        999
    ) AS item_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-12-01',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS item_last_purchase_days

FROM ml_sampled_items_all s

LEFT JOIN data_min d
    ON s.item_id = d.item_id
   AND s.item_category = d.item_category
   AND d.event_time >= '2014-11-25'
   AND d.event_time <  '2014-12-02'

WHERE s.dataset_type = 'valid'

GROUP BY
    s.item_id,
    s.item_category;
INSERT INTO ml_item_feature_7d_all
SELECT
    'test' AS dataset_type,
    '2014-12-11' AS snapshot_date,
    s.item_id,
    s.item_category,

    COUNT(d.behavior_type) AS item_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS item_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS item_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS item_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS item_purchase_count_7d,

    COUNT(DISTINCT d.user_id) AS item_behavior_user_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.user_id END) AS item_purchase_user_count_7d,
    COUNT(DISTINCT LEFT(d.event_time, 10)) AS item_active_days_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_view_to_fav_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_fav_to_cart_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_cart_to_buy_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END), 0),
        4
    ) AS item_view_to_buy_rate_7d,

    COALESCE(
        DATEDIFF('2014-12-11', MAX(LEFT(d.event_time, 10))),
        999
    ) AS item_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-12-11',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS item_last_purchase_days

FROM ml_sampled_items_all s

LEFT JOIN data_min d
    ON s.item_id = d.item_id
   AND s.item_category = d.item_category
   AND d.event_time >= '2014-12-05'
   AND d.event_time <  '2014-12-12'

WHERE s.dataset_type = 'test'

GROUP BY
    s.item_id,
    s.item_category;
CREATE INDEX idx_item_feature
ON ml_item_feature_7d_all(dataset_type, snapshot_date, item_id, item_category);
SELECT
    s.dataset_type,
    COUNT(*) AS sampled_rows,
    COUNT(i.item_id) AS matched_item_feature_rows,
    COUNT(*) - COUNT(i.item_id) AS unmatched_rows
FROM ml_label_buy_7d_sampled s
LEFT JOIN ml_item_feature_7d_all i
    ON s.dataset_type = i.dataset_type
   AND s.snapshot_date = i.snapshot_date
   AND s.item_id = i.item_id
   AND s.item_category = i.item_category
GROUP BY
    s.dataset_type;