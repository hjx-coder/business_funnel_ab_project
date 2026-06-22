-- 02_funnel_analysis.sql
-- 目标：计算整体转化漏斗。

WITH user_step AS (
    SELECT
        user_id,
        MAX(CASE WHEN event_name = 'visit_home' THEN 1 ELSE 0 END) AS visit_home,
        MAX(CASE WHEN event_name = 'view_product' THEN 1 ELSE 0 END) AS view_product,
        MAX(CASE WHEN event_name = 'add_cart' THEN 1 ELSE 0 END) AS add_cart,
        MAX(CASE WHEN event_name = 'submit_order' THEN 1 ELSE 0 END) AS submit_order,
        MAX(CASE WHEN event_name = 'pay_success' THEN 1 ELSE 0 END) AS pay_success
    FROM fact_event
    GROUP BY user_id
),
funnel AS (
    SELECT '1_visit_home' AS step, COUNT(DISTINCT CASE WHEN visit_home = 1 THEN user_id END) AS users FROM user_step
    UNION ALL
    SELECT '2_view_product', COUNT(DISTINCT CASE WHEN view_product = 1 THEN user_id END) FROM user_step
    UNION ALL
    SELECT '3_add_cart', COUNT(DISTINCT CASE WHEN add_cart = 1 THEN user_id END) FROM user_step
    UNION ALL
    SELECT '4_submit_order', COUNT(DISTINCT CASE WHEN submit_order = 1 THEN user_id END) FROM user_step
    UNION ALL
    SELECT '5_pay_success', COUNT(DISTINCT CASE WHEN pay_success = 1 THEN user_id END) FROM user_step
)
SELECT
    step,
    users,
    ROUND(1.0 * users / LAG(users) OVER (ORDER BY step), 4) AS step_conversion_rate,
    ROUND(1.0 * users / FIRST_VALUE(users) OVER (ORDER BY step), 4) AS total_conversion_rate
FROM funnel
ORDER BY step;
