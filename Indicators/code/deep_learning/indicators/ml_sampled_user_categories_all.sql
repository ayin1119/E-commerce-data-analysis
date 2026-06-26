DROP TABLE IF EXISTS ml_sampled_user_categories_all;

CREATE TABLE ml_sampled_user_categories_all AS
SELECT DISTINCT
    dataset_type,
    snapshot_date,
    user_id,
    item_category
FROM ml_label_buy_7d_sampled;
CREATE INDEX idx_sampled_user_category
ON ml_sampled_user_categories_all(dataset_type, snapshot_date, user_id, item_category);
CREATE INDEX idx_data_user_category_time_behavior
ON data_min(user_id, item_category, event_time, behavior_type, item_id);
DROP TABLE IF EXISTS ml_user_category_feature_7d_all;

CREATE TABLE ml_user_category_feature_7d_all (
    dataset_type VARCHAR(20),
    snapshot_date DATE,
    user_id BIGINT,
    item_category BIGINT,

    user_category_total_behavior_count_7d INT,
    user_category_view_count_7d INT,
    user_category_fav_count_7d INT,
    user_category_cart_count_7d INT,
    user_category_purchase_count_7d INT,

    user_category_active_days_7d INT,
    user_category_behavior_item_count_7d INT,
    user_category_purchase_item_count_7d INT,

    user_category_purchase_rate_7d DECIMAL(10,4),
    user_category_cart_rate_7d DECIMAL(10,4),

    user_category_behavior_share_7d DECIMAL(10,4),
    user_category_purchase_share_7d DECIMAL(10,4),

    user_category_last_behavior_days INT,
    user_category_last_purchase_days INT
);
INSERT INTO ml_user_category_feature_7d_all
SELECT
    'train' AS dataset_type,
    '2014-11-24' AS snapshot_date,
    s.user_id,
    s.item_category,

    COUNT(d.behavior_type) AS user_category_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_category_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_category_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_category_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_category_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_category_active_days_7d,
    COUNT(DISTINCT d.item_id) AS user_category_behavior_item_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_id END) AS user_category_purchase_item_count_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_category_purchase_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_category_cart_rate_7d,

    ROUND(
        COUNT(d.behavior_type)
        / NULLIF(u.user_total_behavior_count_7d, 0),
        4
    ) AS user_category_behavior_share_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(u.user_purchase_count_7d, 0),
        4
    ) AS user_category_purchase_share_7d,

    COALESCE(
        DATEDIFF('2014-11-24', MAX(LEFT(d.event_time, 10))),
        999
    ) AS user_category_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-11-24',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS user_category_last_purchase_days

FROM ml_sampled_user_categories_all s

LEFT JOIN data_min d
    ON s.user_id = d.user_id
   AND s.item_category = d.item_category
   AND d.event_time >= '2014-11-18'
   AND d.event_time <  '2014-11-25'

LEFT JOIN ml_user_feature_7d_all u
    ON s.dataset_type = u.dataset_type
   AND s.snapshot_date = u.snapshot_date
   AND s.user_id = u.user_id

WHERE s.dataset_type = 'train'

GROUP BY
    s.user_id,
    s.item_category,
    u.user_total_behavior_count_7d,
    u.user_purchase_count_7d;
INSERT INTO ml_user_category_feature_7d_all
SELECT
    'valid' AS dataset_type,
    '2014-12-01' AS snapshot_date,
    s.user_id,
    s.item_category,

    COUNT(d.behavior_type) AS user_category_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_category_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_category_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_category_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_category_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_category_active_days_7d,
    COUNT(DISTINCT d.item_id) AS user_category_behavior_item_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_id END) AS user_category_purchase_item_count_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_category_purchase_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_category_cart_rate_7d,

    ROUND(
        COUNT(d.behavior_type)
        / NULLIF(u.user_total_behavior_count_7d, 0),
        4
    ) AS user_category_behavior_share_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(u.user_purchase_count_7d, 0),
        4
    ) AS user_category_purchase_share_7d,

    COALESCE(
        DATEDIFF('2014-12-01', MAX(LEFT(d.event_time, 10))),
        999
    ) AS user_category_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-12-01',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS user_category_last_purchase_days

FROM ml_sampled_user_categories_all s

LEFT JOIN data_min d
    ON s.user_id = d.user_id
   AND s.item_category = d.item_category
   AND d.event_time >= '2014-11-25'
   AND d.event_time <  '2014-12-02'

LEFT JOIN ml_user_feature_7d_all u
    ON s.dataset_type = u.dataset_type
   AND s.snapshot_date = u.snapshot_date
   AND s.user_id = u.user_id

WHERE s.dataset_type = 'valid'

GROUP BY
    s.user_id,
    s.item_category,
    u.user_total_behavior_count_7d,
    u.user_purchase_count_7d;
INSERT INTO ml_user_category_feature_7d_all
SELECT
    'test' AS dataset_type,
    '2014-12-11' AS snapshot_date,
    s.user_id,
    s.item_category,

    COUNT(d.behavior_type) AS user_category_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_category_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_category_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_category_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_category_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_category_active_days_7d,
    COUNT(DISTINCT d.item_id) AS user_category_behavior_item_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_id END) AS user_category_purchase_item_count_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_category_purchase_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_category_cart_rate_7d,

    ROUND(
        COUNT(d.behavior_type)
        / NULLIF(u.user_total_behavior_count_7d, 0),
        4
    ) AS user_category_behavior_share_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(u.user_purchase_count_7d, 0),
        4
    ) AS user_category_purchase_share_7d,

    COALESCE(
        DATEDIFF('2014-12-11', MAX(LEFT(d.event_time, 10))),
        999
    ) AS user_category_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-12-11',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS user_category_last_purchase_days

FROM ml_sampled_user_categories_all s

LEFT JOIN data_min d
    ON s.user_id = d.user_id
   AND s.item_category = d.item_category
   AND d.event_time >= '2014-12-05'
   AND d.event_time <  '2014-12-12'

LEFT JOIN ml_user_feature_7d_all u
    ON s.dataset_type = u.dataset_type
   AND s.snapshot_date = u.snapshot_date
   AND s.user_id = u.user_id

WHERE s.dataset_type = 'test'

GROUP BY
    s.user_id,
    s.item_category,
    u.user_total_behavior_count_7d,
    u.user_purchase_count_7d;
CREATE INDEX idx_user_category_feature
ON ml_user_category_feature_7d_all(dataset_type, snapshot_date, user_id, item_category);
SELECT
    s.dataset_type,
    COUNT(*) AS sampled_rows,
    COUNT(uc.user_id) AS matched_user_category_feature_rows,
    COUNT(*) - COUNT(uc.user_id) AS unmatched_rows
FROM ml_label_buy_7d_sampled s
LEFT JOIN ml_user_category_feature_7d_all uc
    ON s.dataset_type = uc.dataset_type
   AND s.snapshot_date = uc.snapshot_date
   AND s.user_id = uc.user_id
   AND s.item_category = uc.item_category
GROUP BY
    s.dataset_type;