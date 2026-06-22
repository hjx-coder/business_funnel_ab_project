-- 04_ab_test_metrics.sql
-- 目标：计算实验组与对照组的支付转化率、GMV 和 ARPU。
-- 显著性检验在 Python 中完成。

WITH user_pay AS (
    SELECT
        a.group_name,
        a.user_id,
        MAX(CASE WHEN e.event_name = 'pay_success' THEN 1 ELSE 0 END) AS is_paid,
        COALESCE(SUM(o.amount), 0) AS gmv
    FROM ab_assignment a
    LEFT JOIN fact_event e ON a.user_id = e.user_id
    LEFT JOIN fact_order o ON a.user_id = o.user_id
    GROUP BY a.group_name, a.user_id
)
SELECT
    group_name,
    COUNT(*) AS users,
    SUM(is_paid) AS paid_users,
    ROUND(1.0 * SUM(is_paid) / COUNT(*), 4) AS pay_rate,
    ROUND(SUM(gmv), 2) AS gmv,
    ROUND(1.0 * SUM(gmv) / COUNT(*), 2) AS arpu
FROM user_pay
GROUP BY group_name
ORDER BY group_name;
