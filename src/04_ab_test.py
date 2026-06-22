"""
04_ab_test.py
执行 A/B 测试分析：支付转化率、GMV、ARPU、双样本比例 Z 检验。

运行：
python src/04_ab_test.py
"""

from pathlib import Path
import sqlite3
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "processed" / "funnel_ab.db"
OUTPUT = ROOT / "outputs"
OUTPUT.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)

ab_sql = """
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
"""

metrics = pd.read_sql_query(ab_sql, conn)
conn.close()

control = metrics[metrics.group_name == "control"].iloc[0]
treatment = metrics[metrics.group_name == "treatment"].iloc[0]

n1, x1 = int(control.users), int(control.paid_users)
n2, x2 = int(treatment.users), int(treatment.paid_users)
p1, p2 = x1 / n1, x2 / n2

p_pool = (x1 + x2) / (n1 + n2)
se = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
z_value = (p2 - p1) / se

# 双侧 p-value。使用 erfc，避免额外依赖 scipy。
p_value = math.erfc(abs(z_value) / math.sqrt(2))

relative_lift = (p2 - p1) / p1
se_diff = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
ci_low = (p2 - p1) - 1.96 * se_diff
ci_high = (p2 - p1) + 1.96 * se_diff

result = pd.DataFrame([{
    "experiment_id": "checkout_opt_202605",
    "control_users": n1,
    "control_paid_users": x1,
    "control_pay_rate": round(p1, 4),
    "treatment_users": n2,
    "treatment_paid_users": x2,
    "treatment_pay_rate": round(p2, 4),
    "absolute_uplift_pp": round((p2 - p1) * 100, 2),
    "relative_lift": round(relative_lift, 4),
    "z_value": round(z_value, 4),
    "p_value": round(p_value, 6),
    "ci_95_low_pp": round(ci_low * 100, 2),
    "ci_95_high_pp": round(ci_high * 100, 2),
    "conclusion": "显著提升，建议灰度放量" if p_value < 0.05 and p2 > p1 else "未达到显著提升，建议继续观察或复盘策略"
}])

metrics.to_csv(OUTPUT / "ab_metrics.csv", index=False, encoding="utf-8-sig")
result.to_csv(OUTPUT / "ab_test_result.csv", index=False, encoding="utf-8-sig")

print("A/B 实验指标")
print(metrics)
print("\n显著性检验结果")
print(result)
