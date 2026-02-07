-- StreamFlow Analytics: Gold Schema
-- Business-ready dimensional model (star schema)

CREATE SCHEMA IF NOT EXISTS gold;

-- Dimension: Date (pre-populated)
CREATE TABLE gold.dim_date (
    date_key        INTEGER PRIMARY KEY,  -- YYYYMMDD format
    full_date       DATE NOT NULL UNIQUE,
    day_of_week     SMALLINT NOT NULL,
    day_name        VARCHAR(10) NOT NULL,
    month           SMALLINT NOT NULL,
    month_name      VARCHAR(10) NOT NULL,
    quarter         SMALLINT NOT NULL,
    year            SMALLINT NOT NULL,
    is_weekend      BOOLEAN NOT NULL
);

-- Dimension: Customer (SCD Type 1)
CREATE TABLE gold.dim_customer (
    customer_key    SERIAL PRIMARY KEY,
    customer_id     VARCHAR(100) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    city            VARCHAR(100),
    state           CHAR(2),
    risk_profile    VARCHAR(20) DEFAULT 'normal',
    valid_from      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Dimension: Store
CREATE TABLE gold.dim_store (
    store_key   SERIAL PRIMARY KEY,
    store_id    VARCHAR(50) NOT NULL UNIQUE,
    name        VARCHAR(200) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    state       CHAR(2) NOT NULL,
    category    VARCHAR(50)
);

-- Dimension: Product
CREATE TABLE gold.dim_product (
    product_key SERIAL PRIMARY KEY,
    product_id  VARCHAR(50) NOT NULL UNIQUE,
    name        VARCHAR(200) NOT NULL,
    category    VARCHAR(100) NOT NULL,
    price       NUMERIC(12,2) NOT NULL
);

-- Fact: Transactions
CREATE TABLE gold.fact_transactions (
    transaction_key BIGSERIAL PRIMARY KEY,
    transaction_id  VARCHAR(100) NOT NULL UNIQUE,
    date_key        INTEGER NOT NULL REFERENCES gold.dim_date(date_key),
    customer_key    INTEGER NOT NULL REFERENCES gold.dim_customer(customer_key),
    store_key       INTEGER NOT NULL REFERENCES gold.dim_store(store_key),
    product_key     INTEGER REFERENCES gold.dim_product(product_key),
    amount          NUMERIC(12,2) NOT NULL,
    fraud_score     NUMERIC(4,3) DEFAULT 0,
    is_fraud        BOOLEAN DEFAULT FALSE,
    transaction_at  TIMESTAMPTZ NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_fact_txn_date ON gold.fact_transactions (date_key);
CREATE INDEX idx_fact_txn_customer ON gold.fact_transactions (customer_key);
CREATE INDEX idx_fact_txn_fraud ON gold.fact_transactions (is_fraud) WHERE is_fraud = TRUE;

-- Fact: Fraud Alerts
CREATE TABLE gold.fact_fraud_alerts (
    alert_key       BIGSERIAL PRIMARY KEY,
    date_key        INTEGER NOT NULL REFERENCES gold.dim_date(date_key),
    customer_key    INTEGER NOT NULL REFERENCES gold.dim_customer(customer_key),
    transaction_id  VARCHAR(100) NOT NULL,
    alert_type      VARCHAR(50) NOT NULL,
    fraud_score     NUMERIC(4,3) NOT NULL,
    rules_triggered TEXT[] NOT NULL,
    detected_at     TIMESTAMPTZ NOT NULL,
    loaded_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Aggregate: Hourly Sales
CREATE TABLE gold.agg_hourly_sales (
    id                  BIGSERIAL PRIMARY KEY,
    hour_timestamp      TIMESTAMPTZ NOT NULL,
    store_key           INTEGER NOT NULL REFERENCES gold.dim_store(store_key),
    transaction_count   INTEGER NOT NULL DEFAULT 0,
    total_amount        NUMERIC(14,2) NOT NULL DEFAULT 0,
    avg_amount          NUMERIC(12,2) NOT NULL DEFAULT 0,
    fraud_count         INTEGER NOT NULL DEFAULT 0,
    computed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (hour_timestamp, store_key)
);

-- Aggregate: Daily Fraud
CREATE TABLE gold.agg_daily_fraud (
    id              BIGSERIAL PRIMARY KEY,
    date_key        INTEGER NOT NULL REFERENCES gold.dim_date(date_key),
    total_alerts    INTEGER NOT NULL DEFAULT 0,
    total_txns      INTEGER NOT NULL DEFAULT 0,
    fraud_rate      NUMERIC(6,4) NOT NULL DEFAULT 0,
    top_rule        VARCHAR(50),
    avg_score       NUMERIC(4,3) DEFAULT 0,
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (date_key)
);
