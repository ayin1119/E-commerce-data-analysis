DROP TABLE IF EXISTS ml_future_purchase_pair_all;

CREATE TABLE ml_future_purchase_pair_all (
    dataset_type VARCHAR(20),
    snapshot_date DATE,
    user_id BIGINT,
    item_id BIGINT
);
INSERT INTO ml_future_purchase_pair_all
SELECT
    'train' AS dataset_type,
    '2014-11-24' AS snapshot_date,
    user_id,
    item_id
FROM data_min
WHERE behavior_type = 4
  AND event_time >= '2014-11-25'
  AND event_time <  '2014-12-02'
GROUP BY
    user_id,
    item_id;
INSERT INTO ml_future_purchase_pair_all
SELECT
    'valid' AS dataset_type,
    '2014-12-01' AS snapshot_date,
    user_id,
    item_id
FROM data_min
WHERE behavior_type = 4
  AND event_time >= '2014-12-02'
  AND event_time <  '2014-12-09'
GROUP BY
    user_id,
    item_id;
INSERT INTO ml_future_purchase_pair_all
SELECT
    'test' AS dataset_type,
    '2014-12-11' AS snapshot_date,
    user_id,
    item_id
FROM data_min
WHERE behavior_type = 4
  AND event_time >= '2014-12-12'
  AND event_time <  '2014-12-19'
GROUP BY
    user_id,
    item_id;
CREATE INDEX idx_future_purchase_pair
ON ml_future_purchase_pair_all(dataset_type, snapshot_date, user_id, item_id);
SELECT
    dataset_type,
    snapshot_date,
    COUNT(*) AS future_purchase_pair_count
FROM ml_future_purchase_pair_all
GROUP BY
    dataset_type,
    snapshot_date
ORDER BY
    snapshot_date;
DROP TABLE IF EXISTS ml_label_buy_7d_all;

CREATE TABLE ml_label_buy_7d_all AS
SELECT
    c.dataset_type,
    c.snapshot_date,
    c.user_id,
    c.item_id,
    c.item_category,

    CASE
        WHEN p.user_id IS NOT NULL THEN 1
        ELSE 0
    END AS label_buy_7d

FROM ml_candidate_user_item_all c

LEFT JOIN ml_future_purchase_pair_all p
    ON c.dataset_type = p.dataset_type
   AND c.snapshot_date = p.snapshot_date
   AND c.user_id = p.user_id
   AND c.item_id = p.item_id;
CREATE INDEX idx_label_user_item
ON ml_label_buy_7d_all(dataset_type, snapshot_date, user_id, item_id);
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
FROM ml_label_buy_7d_all
GROUP BY
    dataset_type,
    label_buy_7d
ORDER BY
    dataset_type,
    label_buy_7d;