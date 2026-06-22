-- 01_create_tables.sql
-- 本脚本为 SQLite 版本，字段设计可迁移到 MySQL。

DROP TABLE IF EXISTS dim_user;
DROP TABLE IF EXISTS fact_event;
DROP TABLE IF EXISTS fact_order;
DROP TABLE IF EXISTS ab_assignment;

CREATE TABLE dim_user (
    user_id INTEGER PRIMARY KEY,
    register_date TEXT,
    channel TEXT,
    device TEXT,
    city_tier TEXT,
    user_type TEXT
);

CREATE TABLE fact_event (
    event_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    session_id TEXT,
    event_time TEXT,
    event_name TEXT,
    product_id INTEGER,
    channel TEXT,
    device TEXT
);

CREATE TABLE fact_order (
    order_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    session_id TEXT,
    product_id INTEGER,
    order_time TEXT,
    amount REAL,
    status TEXT
);

CREATE TABLE ab_assignment (
    user_id INTEGER,
    experiment_id TEXT,
    group_name TEXT,
    strategy_name TEXT,
    assign_time TEXT
);
