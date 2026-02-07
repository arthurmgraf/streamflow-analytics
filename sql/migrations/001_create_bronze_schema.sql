-- StreamFlow Analytics: Bronze Schema
-- Raw, immutable data from Kafka ingestion

CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE bronze.raw_transactions (
    id              BIGSERIAL PRIMARY KEY,
    kafka_topic     VARCHAR(100) NOT NULL,
    kafka_partition SMALLINT NOT NULL,
    kafka_offset    BIGINT NOT NULL,
    event_timestamp TIMESTAMPTZ NOT NULL,
    raw_payload     JSONB NOT NULL,
    ingested_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    schema_version  SMALLINT NOT NULL DEFAULT 1,

    UNIQUE (kafka_topic, kafka_partition, kafka_offset)
);

CREATE INDEX idx_raw_txn_ingested ON bronze.raw_transactions (ingested_at);
CREATE INDEX idx_raw_txn_payload_customer ON bronze.raw_transactions ((raw_payload->>'customer_id'));

CREATE TABLE bronze.raw_fraud_alerts (
    id              BIGSERIAL PRIMARY KEY,
    alert_type      VARCHAR(50) NOT NULL,
    transaction_id  VARCHAR(100) NOT NULL,
    customer_id     VARCHAR(100) NOT NULL,
    fraud_score     NUMERIC(4,3) NOT NULL,
    rules_triggered JSONB NOT NULL,
    raw_payload     JSONB NOT NULL,
    detected_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    schema_version  SMALLINT NOT NULL DEFAULT 1
);

CREATE INDEX idx_fraud_alerts_detected ON bronze.raw_fraud_alerts (detected_at);
CREATE INDEX idx_fraud_alerts_customer ON bronze.raw_fraud_alerts (customer_id);
