-- hau
SELECT
    DATE_FORMAT(d.event_time, '%Y-%m-%d %H:00:00') AS hour_time,
    COUNT(DISTINCT d.user_id) AS active_users_in_hour
FROM data_min d
WHERE d.event_time IS NOT NULL
GROUP BY DATE_FORMAT(d.event_time, '%Y-%m-%d %H:00:00')