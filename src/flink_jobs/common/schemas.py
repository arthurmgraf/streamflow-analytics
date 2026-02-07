"""Flink type info mappings for StreamFlow models."""

from __future__ import annotations

# SQL column definitions for JDBC sinks.
# Used by Flink JDBC connectors to map Python types to SQL types.

BRONZE_RAW_TRANSACTIONS_COLUMNS = [
    ("kafka_topic", "VARCHAR(100)"),
    ("kafka_partition", "SMALLINT"),
    ("kafka_offset", "BIGINT"),
    ("event_timestamp", "TIMESTAMP"),
    ("raw_payload", "VARCHAR"),  # Cast to JSONB in INSERT
    ("schema_version", "SMALLINT"),
]

BRONZE_RAW_FRAUD_ALERTS_COLUMNS = [
    ("alert_type", "VARCHAR(50)"),
    ("transaction_id", "VARCHAR(100)"),
    ("customer_id", "VARCHAR(100)"),
    ("fraud_score", "NUMERIC(4,3)"),
    ("rules_triggered", "VARCHAR"),  # JSON array as text
    ("raw_payload", "VARCHAR"),  # Cast to JSONB in INSERT
]

BRONZE_RAW_TRANSACTIONS_INSERT = (
    "INSERT INTO bronze.raw_transactions "
    "(kafka_topic, kafka_partition, kafka_offset, event_timestamp, raw_payload, schema_version) "
    "VALUES (?, ?, ?, ?, ?::jsonb, ?) "
    "ON CONFLICT (kafka_topic, kafka_partition, kafka_offset) DO NOTHING"
)

BRONZE_RAW_FRAUD_ALERTS_INSERT = (
    "INSERT INTO bronze.raw_fraud_alerts "
    "(alert_type, transaction_id, customer_id, fraud_score, rules_triggered, raw_payload) "
    "VALUES (?, ?, ?, ?, ?::jsonb, ?::jsonb)"
)
