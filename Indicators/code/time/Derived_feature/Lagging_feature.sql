-- 按日期统计总行为和总购买量
CREATE TABLE daily_behavior_summary AS
SELECT
    LEFT(event_time, 10) AS active_date,
    COUNT(*) AS total_behavior,
    SUM(CASE WHEN behavior_type = 4 THEN 1 ELSE 0 END) AS total_purchase
FROM data_min
GROUP BY
    LEFT(event_time, 10);
-- 日期滞后对比分析：将当天数据与未来第1/3/7天的数据进行关联
SELECT
    a.active_date AS behavior_date,

    a.total_behavior AS today_behavior_count,
    a.total_purchase AS today_purchase_count,

    b1.total_purchase AS purchase_after_1d,
    b3.total_purchase AS purchase_after_3d,
    b7.total_purchase AS purchase_after_7d

FROM daily_behavior_summary a

LEFT JOIN daily_behavior_summary b1
    ON b1.active_date = DATE_ADD(a.active_date, INTERVAL 1 DAY)

LEFT JOIN daily_behavior_summary b3
    ON b3.active_date = DATE_ADD(a.active_date, INTERVAL 3 DAY)

LEFT JOIN daily_behavior_summary b7
    ON b7.active_date = DATE_ADD(a.active_date, INTERVAL 7 DAY)

ORDER BY
    a.active_date;