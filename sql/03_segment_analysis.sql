-- 03_segment_analysis.sql
-- 目标：按渠道拆分漏斗，定位低转化来源。

WITH user_step AS (
    SELECT
        u.channel,
        e.user_id,
        MAX(CASE WHEN e.event_name = 'visit_home' THEN 1 ELSE 0 END) AS visit_home,
        MAX(CASE WHEN e.event_name = 'view_product' THEN 1 ELSE 0 END) AS view_product,
        MAX(CASE WHEN e.event_name = 'add_cart' THEN 1 ELSE 0 END) AS add_cart,
        MAX(CASE WHEN e.event_name = 'submit_order' THEN 1 ELSE 0 END) AS submit_order,
        MAX(CASE WHEN e.event_name = 'pay_success' THEN 1 ELSE 0 END) AS pay_success
    FROM fact_event e
    JOIN dim_user u ON e.user_id = u.user_id
    GROUP BY u.channel, e.user_id
)
SELECT
    channel,
    COUNT(DISTINCT CASE WHEN visit_home = 1 THEN user_id END) AS visit_users,
    COUNT(DISTINCT CASE WHEN view_product = 1 THEN user_id END) AS view_users,
    COUNT(DISTINCT CASE WHEN add_cart = 1 THEN user_id END) AS cart_users,
    COUNT(DISTINCT CASE WHEN submit_order = 1 THEN user_id END) AS submit_users,
    COUNT(DISTINCT CASE WHEN pay_success = 1 THEN user_id END) AS pay_users,
    ROUND(1.0 * COUNT(DISTINCT CASE WHEN view_product = 1 THEN user_id END) 
          / COUNT(DISTINCT CASE WHEN visit_home = 1 THEN user_id END), 4) AS visit_to_view_rate,
    ROUND(1.0 * COUNT(DISTINCT CASE WHEN add_cart = 1 THEN user_id END) 
          / COUNT(DISTINCT CASE WHEN view_product = 1 THEN user_id END), 4) AS view_to_cart_rate,
    ROUND(1.0 * COUNT(DISTINCT CASE WHEN pay_success = 1 THEN user_id END) 
          / COUNT(DISTINCT CASE WHEN visit_home = 1 THEN user_id END), 4) AS visit_to_pay_rate
FROM user_step
GROUP BY channel
ORDER BY visit_to_pay_rate DESC;
