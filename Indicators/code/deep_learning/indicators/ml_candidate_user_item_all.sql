DROP TABLE IF EXISTS ml_candidate_user_item_all;

CREATE TABLE ml_candidate_user_item_all (
    dataset_type VARCHAR(20),
    snapshot_date DATE,
    user_id BIGINT,
    item_id BIGINT,
    item_category BIGINT
);
CREATE INDEX idx_ml_event_user_item
ON data_min(event_time, user_id, item_id, item_category);
INSERT INTO ml_candidate_user_item_all
SELECT
    'train' AS dataset_type,
    '2014-11-24' AS snapshot_date,
    user_id,
    item_id,
    MAX(item_category) AS item_category
FROM data_min
WHERE event_time >= '2014-11-18'
  AND event_time <  '2014-11-25'
GROUP BY
    user_id,
    item_id;
    INSERT INTO ml_candidate_user_item_all
SELECT
    'valid' AS dataset_type,
    '2014-12-01' AS snapshot_date,
    user_id,
    item_id,
    MAX(item_category) AS item_category
FROM data_min
WHERE event_time >= '2014-11-25'
  AND event_time <  '2014-12-02'
GROUP BY
    user_id,
    item_id;
    INSERT INTO ml_candidate_user_item_all
SELECT
    'test' AS dataset_type,
    '2014-12-11' AS snapshot_date,
    user_id,
    item_id,
    MAX(item_category) AS item_category
FROM data_min
WHERE event_time >= '2014-12-05'
  AND event_time <  '2014-12-12'
GROUP BY
    user_id,
    item_id;
SELECT
    dataset_type,
    snapshot_date,
    COUNT(*) AS candidate_sample_count
FROM ml_candidate_user_item_all
GROUP BY
    dataset_type,
    snapshot_date
ORDER BY
    snapshot_date;
CREATE INDEX idx_candidate_user_item
ON ml_candidate_user_item_all(dataset_type, snapshot_date, user_id, item_id);