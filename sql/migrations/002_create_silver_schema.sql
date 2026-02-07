-- StreamFlow Analytics: Silver Schema
-- Cleaned, validated, enriched data

CREATE SCHEMA IF NOT EXISTS silver;

CREATE TABLE silver.clean_transactions (
    transaction_id  VARCHAR(100) PRIMARY KEY,
    customer_id     VARCHAR(100) NOT NULL,
    store_id        VARCHAR(50) NOT NULL,
    product_id      VARCHAR(50),
    amount          NUMERIC(12,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'BRL',
    payment_method  VARCHAR(30),
    transaction_at  TIMESTAMPTZ NOT NULL,
    latitude        NUMERIC(9,6),
    longitude       NUMERIC(9,6),
    fraud_score     NUMERIC(4,3) DEFAULT 0.0,
    is_fraud        BOOLEAN DEFAULT FALSE,
    is_valid        BOOLEAN NOT NULL DEFAULT TRUE,
    quality_checks  JSONB,
    cleaned_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_amount_positive CHECK (amount > 0),
    CONSTRAINT chk_fraud_score_range CHECK (fraud_score BETWEEN 0 AND 1)
);

CREATE INDEX idx_clean_txn_customer ON silver.clean_transactions (customer_id);
CREATE INDEX idx_clean_txn_store ON silver.clean_transactions (store_id);
CREATE INDEX idx_clean_txn_timestamp ON silver.clean_transactions (transaction_at);
CREATE INDEX idx_clean_txn_fraud ON silver.clean_transactions (is_fraud) WHERE is_fraud = TRUE;

CREATE TABLE silver.customers (
    customer_id         VARCHAR(100) PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    email               VARCHAR(200),
    city                VARCHAR(100),
    state               CHAR(2),
    avg_transaction_amt NUMERIC(12,2) DEFAULT 0,
    total_transactions  INTEGER DEFAULT 0,
    risk_profile        VARCHAR(20) DEFAULT 'normal',
    first_seen_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE silver.stores (
    store_id    VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    city        VARCHAR(100) NOT NULL,
    state       CHAR(2) NOT NULL,
    latitude    NUMERIC(9,6),
    longitude   NUMERIC(9,6),
    category    VARCHAR(50),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE silver.products (
    product_id  VARCHAR(50) PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    category    VARCHAR(100) NOT NULL,
    price       NUMERIC(12,2) NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
