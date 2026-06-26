-- dau
SELECT
    DATE(event_time) AS date,
    COUNT(DISTINCT user_id) AS active_users_in_day
FROM data_min 
WHERE event_time IS NOT NULL
GROUP BY DATE
