"""
01_generate_data.py
生成可复现的模拟业务数据。

运行：
python src/01_generate_data.py
"""

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

rng = np.random.default_rng(42)
n_users = 5000

channels = ["自然流量", "信息流广告", "搜索广告", "社群裂变", "站内推荐"]
channel_p = np.array([0.30, 0.22, 0.20, 0.13, 0.15])
devices = ["iOS", "Android", "PC"]
device_p = np.array([0.38, 0.48, 0.14])
city_tiers = ["一线", "新一线", "二线", "三线及以下"]
city_p = np.array([0.22, 0.28, 0.28, 0.22])
user_types = ["新用户", "老用户"]
user_type_p = np.array([0.62, 0.38])

user_ids = np.arange(100001, 100001 + n_users)
register_dates = pd.to_datetime("2026-04-01") + pd.to_timedelta(
    rng.integers(0, 61, size=n_users), unit="D"
)

users = pd.DataFrame({
    "user_id": user_ids,
    "register_date": register_dates.strftime("%Y-%m-%d"),
    "channel": rng.choice(channels, size=n_users, p=channel_p),
    "device": rng.choice(devices, size=n_users, p=device_p),
    "city_tier": rng.choice(city_tiers, size=n_users, p=city_p),
    "user_type": rng.choice(user_types, size=n_users, p=user_type_p)
})

ab = pd.DataFrame({
    "user_id": user_ids,
    "experiment_id": "checkout_opt_202605",
    "group_name": rng.choice(["control", "treatment"], size=n_users, p=[0.5, 0.5]),
    "assign_time": "2026-05-01 00:00:00"
})
ab["strategy_name"] = np.where(
    ab["group_name"].eq("treatment"),
    "领券提醒+结算页简化",
    "原始结算流程"
)

event_rows = []
order_rows = []
event_id = 1
order_id = 1
product_ids = np.arange(2001, 2051)
start = pd.Timestamp("2026-05-01 00:00:00")

for _, row in users.iterrows():
    uid = int(row["user_id"])
    group = ab.loc[ab.user_id.eq(uid), "group_name"].iloc[0]
    ch_adj = {"站内推荐": 0.08, "自然流量": 0.04, "搜索广告": 0.02, "信息流广告": -0.02, "社群裂变": -0.04}[row["channel"]]
    dev_adj = {"iOS": 0.03, "Android": 0.00, "PC": -0.03}[row["device"]]
    city_adj = {"一线": 0.03, "新一线": 0.02, "二线": 0.00, "三线及以下": -0.02}[row["city_tier"]]
    old_adj = 0.08 if row["user_type"] == "老用户" else -0.02
    treatment_adj = 0.035 if group == "treatment" else 0.0

    n_sessions = int(rng.choice([1, 2, 3, 4, 5], p=[0.38, 0.28, 0.18, 0.10, 0.06]))

    for s in range(n_sessions):
        session_id = f"S{uid}_{s+1}"
        t = start + pd.to_timedelta(int(rng.integers(0, 31 * 24 * 3600)), unit="s")
        pid = int(rng.choice(product_ids))

        event_rows.append([event_id, uid, session_id, t, "visit_home", pid, row["channel"], row["device"]])
        event_id += 1

        p_view = min(max(0.63 + ch_adj + dev_adj + old_adj / 2, 0.30), 0.90)
        p_cart = min(max(0.28 + ch_adj / 2 + city_adj + old_adj + treatment_adj, 0.08), 0.65)
        p_submit = min(max(0.50 + dev_adj + old_adj / 2 + treatment_adj, 0.18), 0.78)
        p_pay = min(max(0.66 + ch_adj / 2 + city_adj + old_adj + (0.055 if group == "treatment" else 0), 0.25), 0.90)

        if rng.random() < p_view:
            t += pd.to_timedelta(int(rng.integers(20, 600)), unit="s")
            event_rows.append([event_id, uid, session_id, t, "view_product", pid, row["channel"], row["device"]])
            event_id += 1

            if rng.random() < p_cart:
                t += pd.to_timedelta(int(rng.integers(30, 900)), unit="s")
                event_rows.append([event_id, uid, session_id, t, "add_cart", pid, row["channel"], row["device"]])
                event_id += 1

                if rng.random() < p_submit:
                    t += pd.to_timedelta(int(rng.integers(30, 600)), unit="s")
                    event_rows.append([event_id, uid, session_id, t, "submit_order", pid, row["channel"], row["device"]])
                    event_id += 1

                    if rng.random() < p_pay:
                        t += pd.to_timedelta(int(rng.integers(30, 500)), unit="s")
                        event_rows.append([event_id, uid, session_id, t, "pay_success", pid, row["channel"], row["device"]])
                        event_id += 1

                        amount = max(19.9, float(rng.normal(158, 42)))
                        if group == "treatment":
                            amount *= float(rng.normal(1.03, 0.04))

                        order_rows.append([order_id, uid, session_id, pid, t, round(amount, 2), "paid"])
                        order_id += 1

events = pd.DataFrame(
    event_rows,
    columns=["event_id", "user_id", "session_id", "event_time", "event_name", "product_id", "channel", "device"]
)
events["event_time"] = pd.to_datetime(events["event_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

orders = pd.DataFrame(
    order_rows,
    columns=["order_id", "user_id", "session_id", "product_id", "order_time", "amount", "status"]
)
orders["order_time"] = pd.to_datetime(orders["order_time"]).dt.strftime("%Y-%m-%d %H:%M:%S")

users.to_csv(RAW / "users.csv", index=False, encoding="utf-8-sig")
events.to_csv(RAW / "events.csv", index=False, encoding="utf-8-sig")
orders.to_csv(RAW / "orders.csv", index=False, encoding="utf-8-sig")
ab.to_csv(RAW / "ab_assignments.csv", index=False, encoding="utf-8-sig")

print("数据生成完成")
print(f"用户数: {len(users)}")
print(f"事件数: {len(events)}")
print(f"订单数: {len(orders)}")
