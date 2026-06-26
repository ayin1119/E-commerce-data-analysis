DROP TABLE IF EXISTS ml_label_buy_7d_sampled;

CREATE TABLE ml_label_buy_7d_sampled AS
WITH sample_rate AS (
    SELECT
        dataset_type,

        SUM(CASE WHEN label_buy_7d = 1 THEN 1 ELSE 0 END) AS pos_count,
        SUM(CASE WHEN label_buy_7d = 0 THEN 1 ELSE 0 END) AS neg_count,

        LEAST(
            1,
            SUM(CASE WHEN label_buy_7d = 1 THEN 1 ELSE 0 END) * 10
            / NULLIF(SUM(CASE WHEN label_buy_7d = 0 THEN 1 ELSE 0 END), 0)
        ) AS neg_sample_rate

    FROM ml_label_buy_7d_all
    GROUP BY
        dataset_type
)

SELECT
    l.dataset_type,
    l.snapshot_date,
    l.user_id,
    l.item_id,
    l.item_category,
    l.label_buy_7d
FROM ml_label_buy_7d_all l
JOIN sample_rate r
    ON l.dataset_type = r.dataset_type
WHERE l.label_buy_7d = 1

UNION ALL

SELECT
    l.dataset_type,
    l.snapshot_date,
    l.user_id,
    l.item_id,
    l.item_category,
    l.label_buy_7d
FROM ml_label_buy_7d_all l
JOIN sample_rate r
    ON l.dataset_type = r.dataset_type
WHERE l.label_buy_7d = 0
  AND CRC32(CONCAT(l.dataset_type, '_', l.user_id, '_', l.item_id)) / 4294967295 < r.neg_sample_rate;
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
FROM ml_label_buy_7d_sampled
GROUP BY
    dataset_type,
    label_buy_7d
ORDER BY
    dataset_type,
    label_buy_7d;
CREATE INDEX idx_sampled_user_item
ON ml_label_buy_7d_sampled(dataset_type, snapshot_date, user_id, item_id);