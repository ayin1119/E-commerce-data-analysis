DROP TABLE IF EXISTS ml_sampled_users_all;

CREATE TABLE ml_sampled_users_all AS
SELECT DISTINCT
    dataset_type,
    snapshot_date,
    user_id
FROM ml_label_buy_7d_sampled;
CREATE INDEX idx_sampled_users
ON ml_sampled_users_all(dataset_type, snapshot_date, user_id);
CREATE INDEX idx_data_user_time_behavior
ON data_min(user_id, event_time, behavior_type, item_id, item_category);
TRUNCATE TABLE ml_user_feature_7d_all;
INSERT INTO ml_user_feature_7d_all
SELECT
    'train' AS dataset_type,
    '2014-11-24' AS snapshot_date,
    s.user_id,

    COUNT(d.behavior_type) AS user_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_active_days_7d,
    COUNT(DISTINCT d.item_id) AS user_behavior_item_count_7d,
    COUNT(DISTINCT d.item_category) AS user_behavior_category_count_7d,

    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_id END) AS user_purchase_item_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_category END) AS user_purchase_category_count_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_purchase_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_cart_rate_7d,

    COALESCE(
        DATEDIFF('2014-11-24', MAX(LEFT(d.event_time, 10))),
        999
    ) AS user_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-11-24',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS user_last_purchase_days

FROM ml_sampled_users_all s

LEFT JOIN data_min d
    ON s.user_id = d.user_id
   AND d.event_time >= '2014-11-18'
   AND d.event_time <  '2014-11-25'

WHERE s.dataset_type = 'train'

GROUP BY
    s.user_id;
INSERT INTO ml_user_feature_7d_all
SELECT
    'valid' AS dataset_type,
    '2014-12-01' AS snapshot_date,
    s.user_id,

    COUNT(d.behavior_type) AS user_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_active_days_7d,
    COUNT(DISTINCT d.item_id) AS user_behavior_item_count_7d,
    COUNT(DISTINCT d.item_category) AS user_behavior_category_count_7d,

    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_id END) AS user_purchase_item_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_category END) AS user_purchase_category_count_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_purchase_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_cart_rate_7d,

    COALESCE(
        DATEDIFF('2014-12-01', MAX(LEFT(d.event_time, 10))),
        999
    ) AS user_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-12-01',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS user_last_purchase_days

FROM ml_sampled_users_all s

LEFT JOIN data_min d
    ON s.user_id = d.user_id
   AND d.event_time >= '2014-11-25'
   AND d.event_time <  '2014-12-02'

WHERE s.dataset_type = 'valid'

GROUP BY
    s.user_id;
INSERT INTO ml_user_feature_7d_all
SELECT
    'test' AS dataset_type,
    '2014-12-11' AS snapshot_date,
    s.user_id,

    COUNT(d.behavior_type) AS user_total_behavior_count_7d,

    SUM(CASE WHEN d.behavior_type = 1 THEN 1 ELSE 0 END) AS user_view_count_7d,
    SUM(CASE WHEN d.behavior_type = 2 THEN 1 ELSE 0 END) AS user_fav_count_7d,
    SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END) AS user_cart_count_7d,
    SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END) AS user_purchase_count_7d,

    COUNT(DISTINCT LEFT(d.event_time, 10)) AS user_active_days_7d,
    COUNT(DISTINCT d.item_id) AS user_behavior_item_count_7d,
    COUNT(DISTINCT d.item_category) AS user_behavior_category_count_7d,

    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_id END) AS user_purchase_item_count_7d,
    COUNT(DISTINCT CASE WHEN d.behavior_type = 4 THEN d.item_category END) AS user_purchase_category_count_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 4 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_purchase_rate_7d,

    ROUND(
        SUM(CASE WHEN d.behavior_type = 3 THEN 1 ELSE 0 END)
        / NULLIF(COUNT(d.behavior_type), 0),
        4
    ) AS user_cart_rate_7d,

    COALESCE(
        DATEDIFF('2014-12-11', MAX(LEFT(d.event_time, 10))),
        999
    ) AS user_last_behavior_days,

    COALESCE(
        DATEDIFF(
            '2014-12-11',
            MAX(CASE WHEN d.behavior_type = 4 THEN LEFT(d.event_time, 10) END)
        ),
        999
    ) AS user_last_purchase_days

FROM ml_sampled_users_all s

LEFT JOIN data_min d
    ON s.user_id = d.user_id
   AND d.event_time >= '2014-12-05'
   AND d.event_time <  '2014-12-12'

WHERE s.dataset_type = 'test'

GROUP BY
    s.user_id;
CREATE INDEX idx_user_feature
ON ml_user_feature_7d_all(dataset_type, snapshot_date, user_id);
SELECT
    s.dataset_type,
    COUNT(*) AS sampled_rows,
    COUNT(u.user_id) AS matched_user_feature_rows,
    COUNT(*) - COUNT(u.user_id) AS unmatched_rows
FROM ml_label_buy_7d_sampled s
LEFT JOIN ml_user_feature_7d_all u
    ON s.dataset_type = u.dataset_type
   AND s.snapshot_date = u.snapshot_date
   AND s.user_id = u.user_id
GROUP BY
    s.dataset_type;