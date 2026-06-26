-- 计算高峰日的行为量和购买量在全站的占比
SELECT
    peak_day,

    peak_day_behavior_count,
    total_behavior_count,

    ROUND(
        peak_day_behavior_count / NULLIF(total_behavior_count, 0),
        4
    ) AS peak_day_behavior_share,

    CONCAT(
        ROUND(
            peak_day_behavior_count / NULLIF(total_behavior_count, 0) * 100,
            2
        ),
        '%'
    ) AS peak_day_behavior_share_percent,

    peak_day_purchase_count,
    total_purchase_count,

    ROUND(
        peak_day_purchase_count / NULLIF(total_purchase_count, 0),
        4
    ) AS peak_day_purchase_share,

    CONCAT(
        ROUND(
            peak_day_purchase_count / NULLIF(total_purchase_count, 0) * 100,
            2
        ),
        '%'
    ) AS peak_day_purchase_share_percent

FROM (
    SELECT
        '2014-12-12' AS peak_day,

        SUM(
            CASE 
                WHEN LEFT(event_time, 10) = '2014-12-12'
                THEN 1 ELSE 0 
            END
        ) AS peak_day_behavior_count,

        COUNT(*) AS total_behavior_count,

        SUM(
            CASE 
                WHEN LEFT(event_time, 10) = '2014-12-12'
                 AND behavior_type = 4
                THEN 1 ELSE 0 
            END
        ) AS peak_day_purchase_count,

        SUM(
            CASE 
                WHEN behavior_type = 4
                THEN 1 ELSE 0 
            END
        ) AS total_purchase_count

    FROM data_min
) t;