# ADR 005: Astronomer Cosmos for dbt + Airflow Integration

## Status

Accepted

## Date

2026-02-18

## Context

With dbt replacing raw SQL transforms (ADR 004), we need a way to run dbt models
inside Airflow. Three approaches were evaluated:

1. **BashOperator** with `dbt run` — monolithic task, no per-model visibility
2. **Custom PythonOperator** wrapping dbt API — maintenance burden
3. **Astronomer Cosmos** (`DbtTaskGroup`) — industry standard

## Decision

Use **astronomer-cosmos** (v1.13.0+) with `DbtTaskGroup` and
`InvocationMode.SUBPROCESS` to render each dbt model as an individual Airflow task.

Three Cosmos DAGs replace the old PostgresOperator DAGs:

| Old DAG | New DAG | Scope |
|---------|---------|-------|
| `bronze_to_silver` | `dbt_staging` | `models/staging/*` |
| `silver_to_gold` | `dbt_marts` | `models/intermediate/* + models/marts/*` |
| `data_quality` | `dbt_quality` | Singular dbt tests |

## Consequences

### Positive

- **Per-model tasks**: Each dbt model appears as a separate Airflow task
- **Dependency resolution**: Cosmos auto-maps dbt `ref()` to Airflow task dependencies
- **Granular retries**: Failed model retries independently, not the whole DAG
- **Native alerting**: `on_failure_callback` per model, not per DAG
- **Industry standard**: 21M+ monthly downloads, supports Airflow 2.x/3.x

### Negative

- Cosmos adds ~30MB to Airflow Docker image
- `DbtTaskGroup` rendering adds ~5s to DAG parsing
- Requires `install_deps: True` on first run (downloads dbt packages)

## Alternatives Considered

1. **BashOperator** — No per-model visibility, single monolithic task
2. **Custom PythonOperator** — Reinvents Cosmos, more code to maintain
