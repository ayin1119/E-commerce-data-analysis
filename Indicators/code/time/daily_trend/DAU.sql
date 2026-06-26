-- 计算每日活跃用户的日环比和周环比增长率
SELECT
    cur.event_date,
    cur.dau,

    pre.dau AS previous_day_dau,

    ROUND(
        (cur.dau - pre.dau) / NULLIF(pre.dau, 0),
        4
    ) AS day_growth_rate,

    week_pre.dau AS previous_week_dau,

    ROUND(
        (cur.dau - week_pre.dau) / NULLIF(week_pre.dau, 0),
        4
    ) AS week_growth_rate

FROM daily_active_user cur

LEFT JOIN daily_active_user pre
    ON cur.event_date = DATE_ADD(pre.event_date, INTERVAL 1 DAY)

LEFT JOIN daily_active_user week_pre
    ON cur.event_date = DATE_ADD(week_pre.event_date, INTERVAL 7 DAY)

ORDER BY
    cur.event_date;