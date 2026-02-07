# ADR-003: Dead Letter Queue for Malformed Events

## Status
Accepted

## Date
2026-01-25

## Context
The transaction processor currently discards malformed events with a `logger.warning()`. In production, this means lost data that cannot be investigated, no metrics on parsing failure rates, and no way to replay events after a bug fix.

**Options considered:**
1. **Kafka DLQ topic** — Standard pattern, events stay in Kafka ecosystem, configurable retention
2. **S3/GCS bucket** — Cheaper long-term storage, but adds external dependency
3. **Database table** — Queryable, but adds write load to the OLTP database
4. **Discard with enhanced logging** — Simplest, but data is still lost

## Decision
We chose **Kafka DLQ topic** (`streamflow.dlq`) because:

1. **Ecosystem consistency**: Events remain in Kafka; consumers already exist
2. **Replay capability**: DLQ consumers can reprocess events after fixes
3. **Retention control**: 30-day retention (configurable per topic)
4. **Monitoring**: Kafka metrics + Airflow DAG monitors DLQ message count
5. **Side outputs**: Flink `OutputTag` naturally supports routing to DLQ without pipeline branching

## Consequences
- New Kafka topic: `streamflow.dlq` (1 partition, 30-day retention)
- DLQ records include: original event, error type, error message, source topic, timestamp
- Airflow DAG `dlq_monitor.py` checks count every 5 minutes, alerts on threshold
- Schema versioning in serialization layer for forward compatibility
- Events exceeding 1MB truncated before DLQ write
