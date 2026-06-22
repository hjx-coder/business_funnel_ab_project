"""
02_build_database.py
把 CSV 数据写入 SQLite 数据库。

运行：
python src/02_build_database.py
"""

from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

db_path = PROCESSED / "funnel_ab.db"
conn = sqlite3.connect(db_path)

tables = {
    "dim_user": "users.csv",
    "fact_event": "events.csv",
    "fact_order": "orders.csv",
    "ab_assignment": "ab_assignments.csv",
}

for table, filename in tables.items():
    df = pd.read_csv(RAW / filename)
    df.to_sql(table, conn, index=False, if_exists="replace")
    print(f"{table} 写入完成，行数：{len(df)}")

conn.close()
print(f"数据库已生成：{db_path}")
