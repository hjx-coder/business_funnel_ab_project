"""
03_analysis.py
执行漏斗分析、渠道拆分和日趋势分析。

运行：
python src/03_analysis.py
"""

from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "funnel_ab.db"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)

overall_funnel_sql = """
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
"""

channel_sql = """
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
"""

daily_sql = """
WITH daily AS (
    SELECT
        DATE(event_time) AS dt,
        COUNT(DISTINCT CASE WHEN event_name = 'visit_home' THEN user_id END) AS visit_users,
        COUNT(DISTINCT CASE WHEN event_name = 'pay_success' THEN user_id END) AS pay_users
    FROM fact_event
    GROUP BY DATE(event_time)
)
SELECT
    dt,
    visit_users,
    pay_users,
    ROUND(1.0 * pay_users / visit_users, 4) AS daily_pay_rate
FROM daily
ORDER BY dt;
"""

overall = pd.read_sql_query(overall_funnel_sql, conn)
channel = pd.read_sql_query(channel_sql, conn)
daily = pd.read_sql_query(daily_sql, conn)

overall.to_csv(OUTPUT / "overall_funnel.csv", index=False, encoding="utf-8-sig")
channel.to_csv(OUTPUT / "channel_funnel.csv", index=False, encoding="utf-8-sig")
daily.to_csv(OUTPUT / "daily_trend.csv", index=False, encoding="utf-8-sig")

print("整体漏斗")
print(overall)
print("\n渠道漏斗")
print(channel)
print("\n日趋势已输出")
conn.close()
