# ADR 004: dbt Over Raw SQL for Data Transforms

## Status

Accepted

## Date

2026-02-18

## Context

StreamFlow Analytics used raw SQL files executed via Airflow PostgresOperator for all
Bronze→Silver and Silver→Gold transforms. This approach had several issues:

- **No lineage tracking**: No way to see model dependencies or data flow
- **Schema mismatches**: Column names in transform SQL didn't always match DDL
  (e.g., `email` in upsert_dim_customer.sql but not in gold.dim_customer DDL)
- **No incremental testing**: Quality checks ran separately from transforms
- **No schema evolution**: Adding columns required manual DDL + SQL changes

## Decision

Replace all raw SQL transforms with **dbt-core + dbt-postgres**:

- `models/staging/` → Silver schema (incremental, from Bronze sources)
- `models/intermediate/` → Silver schema (customer aggregations)
- `models/marts/` → Gold schema (dimensions, facts, aggregates)
- Custom `generate_schema_name` macro routes models to correct PG schemas
- Schema tests (unique, not_null, accepted_range) co-located with models
- Singular tests for business rules (positive amounts, data freshness)

## Consequences

### Positive

- **Lineage**: dbt generates a full dependency DAG
- **Testing**: Schema + singular tests validate data at every layer
- **Incremental**: `is_incremental()` macro handles watermark-based processing
- **Self-documenting**: YAML schemas serve as living documentation
- **Industry standard**: dbt is the de facto tool for analytics engineering

### Negative

- Additional dependency (dbt-core, dbt-postgres)
- Airflow image grows ~50MB (dbt + cosmos)
- Team must learn dbt conventions (ref, source, config blocks)

## Alternatives Considered

1. **Keep raw SQL + add tests separately** — Doesn't fix lineage or schema issues
2. **SQLMesh** — Less mature ecosystem, smaller community
3. **Spark SQL transforms** — Overkill for batch transforms on PostgreSQL
