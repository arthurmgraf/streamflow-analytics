# DESIGN: End-to-End Production Deploy + dbt Integration

> Technical design for containerizing StreamFlow Analytics, integrating dbt via Cosmos, and achieving 15/15 Staff Engineer portfolio readiness.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | E2E_PRODUCTION |
| **Date** | 2026-02-18 |
| **Author** | design-agent + the-planner |
| **DEFINE** | [DEFINE_E2E_PRODUCTION.md](./DEFINE_E2E_PRODUCTION.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                    STREAMFLOW ANALYTICS — PRODUCTION ARCHITECTURE            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────┐    ┌───────────────────┐    ┌─────────────────────────┐    │
│  │  Generator   │    │   Kafka (Strimzi) │    │  Flink (PyFlink)       │    │
│  │  (K8s Deploy)│───▶│  transactions.raw │───▶│  fraud_detector.py     │    │
│  │             │    │  fraud.alerts     │◀───│  transaction_proc.py   │    │
│  │  Docker:    │    │  metrics.realtime │    │  realtime_agg.py       │    │
│  │  generator  │    │  dlq.errors       │    │                         │    │
│  └─────────────┘    └───────────────────┘    │  Docker: pyflink        │    │
│                                               │  State: RocksDB         │    │
│                                               └───────────┬─────────────┘    │
│                                                           │ JDBC Sink        │
│                                                           ▼                  │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                    PostgreSQL (CloudNativePG)                          │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────────┐  │   │
│  │  │ bronze.*     │  │ silver.*     │  │ gold.*                     │  │   │
│  │  │ raw_txns     │  │ clean_txns   │  │ dim_customer, dim_store    │  │   │
│  │  │ raw_alerts   │  │ customers    │  │ fct_transactions           │  │   │
│  │  │ (Flink sink) │  │ (dbt staging)│  │ fct_fraud_alerts           │  │   │
│  │  └──────┬───────┘  └──────▲───────┘  │ agg_hourly, agg_daily     │  │   │
│  │         │                 │           │ (dbt marts)                │  │   │
│  │         │    dbt run      │           └────────────▲───────────────┘  │   │
│  │         └─────────────────┘                        │                  │   │
│  └────────────────────────────────────────────────────┼──────────────────┘   │
│                                                       │                      │
│  ┌────────────────────────────────────────────────────┼──────────────────┐   │
│  │              Airflow + Astronomer Cosmos            │                  │   │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌───────┴────────┐        │   │
│  │  │ dbt_staging    │  │ dbt_marts       │  │ dbt_quality    │        │   │
│  │  │ (DbtTaskGroup) │─▶│ (DbtTaskGroup)  │  │ (DbtTestOp)    │        │   │
│  │  │ @hourly        │  │ @hourly         │  │ */15 min       │        │   │
│  │  └────────────────┘  └─────────────────┘  └────────────────┘        │   │
│  │                                                                      │   │
│  │  Docker: airflow-dbt (Airflow + dbt-core + cosmos + dbt-postgres)   │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │  Infrastructure: K3s single-node (15.235.61.251)                     │   │
│  │  Namespaces: streamflow-kafka, -processing, -data, -orchestration   │   │
│  │  IaC: Terraform/Terragrunt | GitOps: ArgoCD | CI: GitHub Actions    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Purpose | Technology | Docker Image |
|-----------|---------|------------|--------------|
| Generator | Produce synthetic fraud transactions to Kafka | Python + confluent-kafka | `streamflow/generator:latest` |
| Kafka | Event streaming backbone | Strimzi Kafka Operator (KRaft) | Strimzi official |
| Flink | Real-time fraud detection + Bronze ingestion | PyFlink 1.20 + RocksDB | `streamflow/pyflink:latest` |
| PostgreSQL | Medallion data store (Bronze/Silver/Gold) | CloudNativePG | CNPG official |
| Airflow | Orchestrate dbt transforms | Airflow 2.x + Cosmos | `streamflow/airflow-dbt:latest` |
| dbt | SQL transforms (staging, intermediate, marts) | dbt-core + dbt-postgres | Embedded in Airflow image |

---

## Key Decisions

### Decision 1: Astronomer Cosmos for dbt + Airflow Integration

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** Need to run dbt models inside Airflow with per-model visibility and dependency management.

**Choice:** Use `astronomer-cosmos` (v1.13.0) with `DbtTaskGroup` and `InvocationMode.SUBPROCESS`.

**Rationale:** Cosmos renders each dbt model as an individual Airflow task, providing full lineage visibility in the Airflow UI. It's the industry standard (21M+ monthly downloads), supports Airflow 2.x/3.x, and eliminates the need for custom operators.

**Alternatives Rejected:**
1. BashOperator with `dbt run` — No per-model visibility, single monolithic task, no retry granularity
2. Custom PythonOperator wrapping dbt API — Reinvents Cosmos, more maintenance burden

**Consequences:**
- Airflow Docker image grows (~50MB for cosmos + dbt)
- Gain: Per-model tasks, auto-dependency graph, native Airflow alerting per model

---

### Decision 2: PyFlink Docker Image Without Java JAR Build

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** Current FlinkDeployment references `streamflow-jobs.jar` which doesn't exist. Need a way to run PyFlink code on Flink K8s Operator.

**Choice:** Use the built-in `flink-python_2.12-1.20.0.jar` (PythonDriver) already included in `flink:1.20` image. Create custom Docker image adding Python 3.12 + PyFlink + source code.

**Rationale:** The Flink K8s Operator natively supports Python jobs via `PythonDriver` entryClass. The JAR already exists in `/opt/flink/opt/`. No Maven/Gradle build needed. Verified in official Flink Kubernetes Operator examples.

**Alternatives Rejected:**
1. Maven fat JAR with PyFlink — Adds Java build complexity, 10+ minutes build time, fragile
2. Replace Flink with Python Kafka consumer — Loses Flink checkpointing, state management, exactly-once

**Consequences:**
- Accept: Flink image is larger (~1.5GB with Python + PyFlink + scikit-learn)
- Gain: Zero Java toolchain, simple Dockerfile, standard Flink Operator patterns

---

### Decision 3: K3s Local Image Import (No Registry)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** Need to get custom Docker images onto K3s single-node cluster. Options: ghcr.io, local registry, or direct import.

**Choice:** Build images locally with Docker, save as tarball, import via `sudo k3s ctr images import`. Use `imagePullPolicy: Never` in K8s manifests.

**Rationale:** Simplest approach for single-node K3s. No registry server needed, no network dependency, zero cost. For CI/CD: GitHub Actions builds image, saves as artifact, deploy script SCPs and imports.

**Alternatives Rejected:**
1. ghcr.io — Adds external dependency, slower pull on deploy, needs credentials
2. Local K3s registry — Extra component to manage, uses RAM/CPU

**Consequences:**
- Accept: Image updates require manual import (or deploy script)
- Gain: Zero infrastructure overhead, works offline, fastest local deploy

---

### Decision 4: dbt Schema Routing via Custom Macro

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** dbt defaults to writing all models to a single schema. StreamFlow uses separate schemas: `bronze`, `silver`, `gold`.

**Choice:** Custom `generate_schema_name` macro that routes models based on directory:
- `models/staging/` → `silver` schema
- `models/intermediate/` → `silver` schema
- `models/marts/` → `gold` schema

**Rationale:** dbt's built-in `generate_schema_name` macro can be overridden per project. This is the standard dbt pattern for Medallion architecture with PostgreSQL schemas.

**Alternatives Rejected:**
1. Separate dbt projects per schema — Over-complex, breaks lineage
2. Hardcoded schema in each model — Not DRY, error-prone

**Consequences:**
- Accept: Custom macro adds indirection
- Gain: Models automatically land in correct schema, clean separation

---

### Decision 5: Minimal Resource Deployment (No Monitoring Stack)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** K3s server has ~5.7GB free RAM. Full stack (Kafka + Flink + PG + Airflow + Prometheus + Grafana) would exceed budget.

**Choice:** Deploy core pipeline only. Monitoring via Airflow UI (DAG status, task logs) and `kubectl logs`. No Prometheus/Grafana pods.

**Rationale:** Core pipeline needs ~3.5GB RAM. Prometheus + Grafana would add ~1.5GB, leaving no headroom. Airflow UI provides sufficient operational visibility for a portfolio project.

**Alternatives Rejected:**
1. Full Prometheus + Grafana — OOM risk, K3s instability
2. Prometheus only (no Grafana) — Still ~800MB, marginal benefit without dashboards

**Consequences:**
- Accept: No metrics dashboards, no alerts via AlertManager
- Gain: Stable pipeline with headroom, core functionality proven

---

## Data Flow

```text
1. Generator Python (K8s Deployment)
   │  Produces synthetic transactions: customer_id, amount, lat/lon, store_id
   │  Injects 2% fraud patterns (velocity, geographic, high-value)
   │  Rate: configurable via config/default.yaml (default 100 events/sec)
   │
   ▼
2. Kafka (Strimzi) — Topic: transactions.raw
   │  3 partitions, replication-factor 1, retention 24h
   │
   ▼
3. Flink PyFlink — fraud_detector.py
   │  KeyedProcessFunction per customer_id
   │  5 rules + ML (Isolation Forest) → fraud_score
   │  State: RocksDB with incremental checkpoints (60s interval)
   │  Output: Bronze tables via JDBC sink + fraud alerts to fraud.alerts topic
   │
   ▼
4. PostgreSQL (CloudNativePG) — bronze schema
   │  raw_transactions: JSONB payload from Kafka
   │  raw_fraud_alerts: fraud events from Flink
   │
   ▼
5. Airflow + Cosmos — dbt_staging DAG (@hourly)
   │  dbt run --select staging.*
   │  Models: stg_transactions, stg_fraud_alerts → silver schema
   │  Tests: not_null, unique, accepted_values
   │
   ▼
6. Airflow + Cosmos — dbt_marts DAG (@hourly, after staging)
   │  dbt run --select intermediate.* marts.*
   │  Models: int_customer_stats, dim_customer, dim_store,
   │          fct_transactions, fct_fraud_alerts,
   │          agg_hourly_sales, agg_daily_fraud → gold schema
   │  Tests: relationships, not_null, unique
   │
   ▼
7. Gold Layer — Queryable analytics
   │  Star schema: dimensions + facts + aggregates
   │  Ready for BI tools, dashboards, or SQL queries
   │
   ▼
8. Airflow + Cosmos — dbt_quality DAG (*/15 min)
      dbt test + singular tests (freshness, null_rate, duplicates, amounts)
      Alerts via on_failure_callback
```

---

## File Manifest

### Phase 1: Containerization (7 files)

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 1.1 | `docker/flink/Dockerfile` | Create | PyFlink 1.20 + Python 3.12 + scikit-learn + source code | None |
| 1.2 | `docker/generator/Dockerfile` | Create | Python 3.12 + confluent-kafka + generators | None |
| 1.3 | `docker/airflow/Dockerfile` | Create | Airflow 2.x + dbt-core + dbt-postgres + cosmos | None |
| 1.4 | `scripts/build_images.sh` | Create | Build all 3 Docker images | 1.1, 1.2, 1.3 |
| 1.5 | `scripts/import_images.sh` | Create | `k3s ctr images import` for all images | 1.4 |
| 1.6 | `k8s/flink/fraud-detector.yaml` | Modify | PyFlink app mode (PythonDriver, no custom JAR) | 1.1 |
| 1.7 | `k8s/flink/transaction-processor.yaml` | Modify | PyFlink app mode | 1.1 |
| 1.8 | `k8s/flink/realtime-aggregator.yaml` | Modify | PyFlink app mode | 1.1 |
| 1.9 | `k8s/generator/deployment.yaml` | Create | Generator as K8s Deployment | 1.2 |
| 1.10 | `.github/workflows/ci.yaml` | Modify | Add Docker build validation job | 1.1, 1.2, 1.3 |

### Phase 2: dbt Project (16 files)

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 2.1 | `dbt/dbt_project.yml` | Create | dbt project configuration | None |
| 2.2 | `dbt/profiles.yml` | Create | PostgreSQL connection profile | None |
| 2.3 | `dbt/packages.yml` | Create | dbt-utils dependency | None |
| 2.4 | `dbt/models/staging/_staging__sources.yml` | Create | Bronze source definitions | None |
| 2.5 | `dbt/models/staging/_staging__schema.yml` | Create | Staging model tests | 2.6, 2.7 |
| 2.6 | `dbt/models/staging/stg_transactions.sql` | Create | Bronze → Silver: clean transactions | 2.4 |
| 2.7 | `dbt/models/staging/stg_fraud_alerts.sql` | Create | Bronze → Silver: fraud alerts | 2.4 |
| 2.8 | `dbt/models/intermediate/int_customer_stats.sql` | Create | Customer aggregate stats | 2.6 |
| 2.9 | `dbt/models/intermediate/_intermediate__schema.yml` | Create | Intermediate model tests | 2.8 |
| 2.10 | `dbt/models/marts/dim_customer.sql` | Create | Gold: customer dimension | 2.8 |
| 2.11 | `dbt/models/marts/dim_store.sql` | Create | Gold: store dimension | 2.6 |
| 2.12 | `dbt/models/marts/fct_transactions.sql` | Create | Gold: transaction facts | 2.6, 2.10, 2.11 |
| 2.13 | `dbt/models/marts/fct_fraud_alerts.sql` | Create | Gold: fraud alert facts | 2.7, 2.10 |
| 2.14 | `dbt/models/marts/agg_hourly_sales.sql` | Create | Gold: hourly sales aggregate | 2.12 |
| 2.15 | `dbt/models/marts/agg_daily_fraud.sql` | Create | Gold: daily fraud aggregate | 2.13 |
| 2.16 | `dbt/models/marts/_marts__schema.yml` | Create | Marts model tests | 2.10-2.15 |
| 2.17 | `dbt/tests/assert_positive_amounts.sql` | Create | Singular test: amounts > 0 | 2.6 |
| 2.18 | `dbt/tests/assert_freshness.sql` | Create | Singular test: data < 2h old | 2.6 |
| 2.19 | `dbt/macros/generate_schema_name.sql` | Create | Route models to correct PG schema | None |

### Phase 3: Airflow + Cosmos DAGs (5 files)

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 3.1 | `src/dags/dbt_staging.py` | Create | Cosmos DbtTaskGroup for staging models | Phase 2 |
| 3.2 | `src/dags/dbt_marts.py` | Create | Cosmos DbtTaskGroup for marts models | 3.1 |
| 3.3 | `src/dags/dbt_quality.py` | Create | Cosmos DbtTestLocalOperator for tests | Phase 2 |
| 3.4 | `src/dags/bronze_to_silver.py` | Delete | Replaced by dbt_staging | 3.1 |
| 3.5 | `src/dags/silver_to_gold.py` | Delete | Replaced by dbt_marts | 3.2 |
| 3.6 | `src/dags/data_quality.py` | Delete | Replaced by dbt_quality | 3.3 |
| 3.7 | `tests/unit/test_dbt_dags.py` | Create | DAG import + structure tests | 3.1, 3.2, 3.3 |

### Phase 4: End-to-End Integration (5 files)

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 4.1 | `scripts/deploy.sh` | Modify | v2: image build + import + deploy + verify | Phase 1 |
| 4.2 | `scripts/setup_k3s.sh` | Create | One-time K3s node preparation | None |
| 4.3 | `scripts/demo.sh` | Create | One-command full pipeline demo | 4.1 |
| 4.4 | `infra/modules/airflow/main.tf` | Modify | Add dbt/cosmos deps, DAG sync, connection | None |
| 4.5 | `pyproject.toml` | Modify | Add dbt + cosmos to optional deps | None |

### Phase 5: Staff Polish (7 files)

| # | File | Action | Purpose | Dependencies |
|---|------|--------|---------|--------------|
| 5.1 | `README.md` | Modify | Updated architecture, dbt section, demo instructions | All phases |
| 5.2 | `docs/adr/013-dbt-over-raw-sql.md` | Create | ADR: why dbt replaces raw SQL | None |
| 5.3 | `docs/adr/014-cosmos-airflow-integration.md` | Create | ADR: why Cosmos over BashOperator | None |
| 5.4 | `docs/adr/015-pyflink-docker-no-jar.md` | Create | ADR: PyFlink without Java JAR | None |
| 5.5 | `docs/SETUP_GUIDE.md` | Modify | Real deploy instructions | Phase 4 |
| 5.6 | `docs/RUNBOOK.md` | Modify | Updated operational procedures | Phase 4 |
| 5.7 | `.github/workflows/ci.yaml` | Modify | Add dbt compile + test validation | Phase 2 |

**Total Files: 40** (28 create + 9 modify + 3 delete)

---

## Code Patterns

### Pattern 1: Cosmos DbtTaskGroup DAG

```python
"""Airflow DAG: dbt staging transforms via Cosmos."""
from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, RenderConfig
from cosmos.constants import InvocationMode
from cosmos.profiles import PostgresUserPasswordProfileMapping

DBT_PROJECT_PATH = Path("/opt/airflow/dbt")

profile_config = ProfileConfig(
    profile_name="streamflow",
    target_name="prod",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="streamflow_postgres",
        profile_args={"schema": "silver"},
    ),
)

with DAG(
    dag_id="dbt_staging",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "dbt", "staging"],
    max_active_runs=1,
    default_args={
        "owner": "streamflow",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
) as dag:
    staging = DbtTaskGroup(
        group_id="staging",
        project_config=ProjectConfig(dbt_project_path=str(DBT_PROJECT_PATH)),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            invocation_mode=InvocationMode.SUBPROCESS,
        ),
        render_config=RenderConfig(
            select=["path:models/staging"],
        ),
        operator_args={"install_deps": True},
    )
```

### Pattern 2: dbt Staging Model (Incremental)

```sql
-- models/staging/stg_transactions.sql
{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        schema='silver',
        on_schema_change='append_new_columns'
    )
}}

with source as (
    select * from {{ source('bronze', 'raw_transactions') }}
    {% if is_incremental() %}
    where ingested_at > (select coalesce(max(cleaned_at), '1970-01-01'::timestamptz) from {{ this }})
    {% endif %}
),

fraud_scores as (
    select
        transaction_id,
        max(fraud_score) as max_score
    from {{ source('bronze', 'raw_fraud_alerts') }}
    group by transaction_id
),

cleaned as (
    select
        s.raw_payload->>'transaction_id'                      as transaction_id,
        s.raw_payload->>'customer_id'                         as customer_id,
        s.raw_payload->>'store_id'                            as store_id,
        (s.raw_payload->>'amount')::numeric(12,2)             as amount,
        coalesce(s.raw_payload->>'currency', 'BRL')           as currency,
        (s.raw_payload->>'timestamp')::timestamptz            as transaction_at,
        (s.raw_payload->>'latitude')::numeric(9,6)            as latitude,
        (s.raw_payload->>'longitude')::numeric(9,6)           as longitude,
        coalesce(f.max_score, 0.0)                            as fraud_score,
        coalesce(f.max_score, 0.0) > 0.7                     as is_fraud,
        (s.raw_payload->>'transaction_id') is not null
            and (s.raw_payload->>'amount')::numeric > 0       as is_valid,
        now()                                                 as cleaned_at
    from source s
    left join fraud_scores f
        on f.transaction_id = s.raw_payload->>'transaction_id'
)

select * from cleaned
```

### Pattern 3: dbt Schema Test Definition

```yaml
# models/staging/_staging__schema.yml
version: 2

models:
  - name: stg_transactions
    description: "Cleaned transactions from Bronze raw_transactions"
    columns:
      - name: transaction_id
        description: "Unique transaction identifier"
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              inclusive: false
      - name: is_valid
        tests:
          - accepted_values:
              values: [true, false]
```

### Pattern 4: Custom Schema Routing Macro

```sql
-- macros/generate_schema_name.sql
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is not none -%}
        {{ custom_schema_name | trim }}
    {%- elif node.fqn[1] == 'staging' -%}
        silver
    {%- elif node.fqn[1] == 'intermediate' -%}
        silver
    {%- elif node.fqn[1] == 'marts' -%}
        gold
    {%- else -%}
        {{ target.schema }}
    {%- endif -%}
{%- endmacro %}
```

### Pattern 5: PyFlink Dockerfile (Multi-Stage)

```dockerfile
# docker/flink/Dockerfile
FROM flink:1.20-java17 AS base

USER root

# Install Python 3.12
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip python3-dev && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    rm -rf /var/lib/apt/lists/*

# Install PyFlink + ML deps
RUN pip3 install --no-cache-dir \
    apache-flink==1.20.0 \
    confluent-kafka \
    scikit-learn \
    joblib \
    pydantic \
    pyyaml

# Copy source code
COPY src/flink_jobs/ /opt/flink/usrlib/src/flink_jobs/
COPY src/models/ /opt/flink/usrlib/src/models/
COPY src/utils/ /opt/flink/usrlib/src/utils/
COPY config/ /opt/flink/usrlib/config/

# Copy ML model if exists
COPY models/ /opt/flink/usrlib/models/ 2>/dev/null || true

RUN chown -R flink:flink /opt/flink/usrlib/
USER flink

WORKDIR /opt/flink
```

### Pattern 6: FlinkDeployment PyFlink Mode

```yaml
# k8s/flink/fraud-detector.yaml (updated)
apiVersion: flink.apache.org/v1beta1
kind: FlinkDeployment
metadata:
  name: fraud-detector
  namespace: streamflow-processing
spec:
  image: streamflow/pyflink:latest
  imagePullPolicy: Never  # Local K3s import
  flinkVersion: v1_20
  flinkConfiguration:
    taskmanager.numberOfTaskSlots: "2"
    state.backend: rocksdb
    state.backend.rocksdb.memory.managed: "true"
    state.backend.incremental: "true"
    execution.checkpointing.interval: "60000"
    execution.checkpointing.mode: EXACTLY_ONCE
    python.executable: /usr/bin/python3
  serviceAccount: flink
  podTemplate:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 9999
        fsGroup: 9999
      containers:
        - name: flink-main-container
          securityContext:
            allowPrivilegeEscalation: false
            capabilities:
              drop: ["ALL"]
  jobManager:
    resource:
      memory: "512Mi"
      cpu: 0.1
  taskManager:
    resource:
      memory: "768Mi"
      cpu: 0.2
    replicas: 1
  job:
    jarURI: local:///opt/flink/opt/flink-python_2.12-1.20.0.jar
    entryClass: org.apache.flink.client.python.PythonDriver
    args:
      - "-pyclientexec"
      - "/usr/bin/python3"
      - "-py"
      - "/opt/flink/usrlib/src/flink_jobs/fraud_detector.py"
    parallelism: 2
    upgradeMode: savepoint
```

### Pattern 7: Build & Import Script

```bash
#!/usr/bin/env bash
# scripts/build_images.sh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TAG="${1:-latest}"

echo "Building streamflow/pyflink:${TAG}..."
docker build -t "streamflow/pyflink:${TAG}" -f "$PROJECT_DIR/docker/flink/Dockerfile" "$PROJECT_DIR"

echo "Building streamflow/generator:${TAG}..."
docker build -t "streamflow/generator:${TAG}" -f "$PROJECT_DIR/docker/generator/Dockerfile" "$PROJECT_DIR"

echo "Building streamflow/airflow-dbt:${TAG}..."
docker build -t "streamflow/airflow-dbt:${TAG}" -f "$PROJECT_DIR/docker/airflow/Dockerfile" "$PROJECT_DIR"

echo "All images built successfully."
echo "To import to K3s: ./scripts/import_images.sh ${TAG}"
```

---

## Integration Points

| External System | Integration Type | Authentication | Notes |
|-----------------|-----------------|----------------|-------|
| Kafka (Strimzi) | Kafka protocol (PLAINTEXT) | None (internal K8s) | Internal cluster DNS |
| PostgreSQL (CNPG) | JDBC / psycopg2 | Secret (auto-generated by CNPG) | `streamflow-pg-superuser` K8s secret |
| Flink Operator | K8s CRD (FlinkDeployment) | ServiceAccount | `flink` SA in `streamflow-processing` |
| Airflow | Helm chart (Astronomer) | Webserver login | Default admin/admin for portfolio |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal |
|-----------|-------|-------|-------|---------------|
| Unit (Python) | Fraud rules, generators, state | `tests/unit/*.py` | pytest + mock | 80%+ |
| Contract | Schema compatibility | `tests/contract/*.py` | pytest + pydantic | All schemas |
| Integration | ML pipeline, dbt models | `tests/integration/*.py` | pytest | Key paths |
| DAG import | Airflow DAG syntax | `tests/unit/test_dbt_dags.py` | pytest + airflow | All DAGs |
| dbt tests | Data quality (schema + singular) | `dbt/models/**/*.yml`, `dbt/tests/*.sql` | dbt test | 15+ tests |
| dbt compile | dbt project validity | CI job | `dbt compile` | Must pass |
| E2E smoke | Full pipeline flow | `scripts/demo.sh` | bash + psql | Happy path |
| Docker build | Image builds successfully | CI job | `docker build` | All 3 images |

---

## Error Handling

| Error Type | Handling Strategy | Retry? |
|------------|-------------------|--------|
| Flink checkpoint failure | Exponential backoff restart (10s → 2min) | Yes (auto) |
| dbt model failure | Cosmos retry per-task (2 retries, 2min delay) | Yes (per model) |
| Kafka connectivity loss | Flink auto-reconnect with backoff | Yes (auto) |
| PostgreSQL connection drop | Airflow retries with pool recycling | Yes (2 retries) |
| dbt test failure | on_failure_callback logs alert, DAG fails | No (alerts) |
| Docker build failure | CI job fails, blocks deploy | No (fix code) |
| K3s OOM | Pod evicted, kubelet restarts | Yes (K8s restart) |

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `STREAMFLOW_ENV` | string | `production` | Environment name (Flink + generators) |
| `DBT_PROJECT_PATH` | string | `/opt/airflow/dbt` | Path to dbt project in Airflow container |
| `AIRFLOW__CORE__DAGS_FOLDER` | string | `/opt/airflow/dags` | DAG folder in Airflow container |
| `streamflow_postgres` | Airflow Connection | K8s secret | PostgreSQL connection for dbt + DAGs |
| `generator.events_per_second` | int | 100 | Generator throughput |
| `generator.fraud_rate` | float | 0.02 | Fraction of fraudulent transactions |

---

## Security Considerations

- All pods run as non-root (`runAsNonRoot: true`, `runAsUser: 9999`)
- All containers drop ALL capabilities
- PostgreSQL credentials via K8s Secrets (auto-generated by CNPG)
- Airflow webserver: default credentials acceptable for portfolio (not public-facing)
- `imagePullPolicy: Never` prevents accidental pull from public registries
- NetworkPolicies isolate namespaces (already in `k8s/security/`)

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| Logging | Structured JSON via Python logging (already implemented) |
| DAG monitoring | Airflow UI — per-model dbt task status, SLA tracking |
| Flink monitoring | `kubectl logs` + Flink Web UI (port-forward 8081) |
| Data quality | dbt tests via Cosmos — failure triggers on_failure_callback |
| Pipeline health | `scripts/demo.sh` runs smoke test after deploy |

---

## Resource Budget (K3s 5.7GB Free RAM)

| Component | Memory Request | Memory Limit | CPU Request |
|-----------|---------------|-------------|-------------|
| Kafka (Strimzi) | 512Mi | 1Gi | 0.2 |
| Flink JobManager | 512Mi | 512Mi | 0.1 |
| Flink TaskManager | 768Mi | 768Mi | 0.2 |
| PostgreSQL (CNPG) | 256Mi | 512Mi | 0.1 |
| Airflow (webserver + scheduler) | 512Mi | 1Gi | 0.2 |
| Generator | 128Mi | 256Mi | 0.1 |
| K3s system overhead | ~500Mi | — | 0.2 |
| **TOTAL** | **~3.2Gi** | **~4Gi** | **~1.1** |
| **Available** | **5.7Gi** | | **4 cores** |
| **Headroom** | **~2.5Gi** | | **~2.9** |

---

## Build Order (Dependency Graph)

```text
Phase 1 (Containerization)
├── 1.1 docker/flink/Dockerfile          ← No deps
├── 1.2 docker/generator/Dockerfile      ← No deps
├── 1.3 docker/airflow/Dockerfile        ← No deps
├── 1.4 scripts/build_images.sh          ← 1.1, 1.2, 1.3
├── 1.5 scripts/import_images.sh         ← 1.4
├── 1.6-1.8 k8s/flink/*.yaml (modify)   ← 1.1
├── 1.9 k8s/generator/deployment.yaml    ← 1.2
└── 1.10 .github/workflows/ci.yaml      ← 1.1, 1.2, 1.3

Phase 2 (dbt Project)  ← Can parallel with Phase 1
├── 2.1 dbt_project.yml                  ← No deps
├── 2.2 profiles.yml                     ← No deps
├── 2.3 packages.yml                     ← No deps
├── 2.4 _staging__sources.yml            ← No deps
├── 2.6-2.7 staging models               ← 2.4
├── 2.8 intermediate model               ← 2.6
├── 2.10-2.15 marts models               ← 2.6, 2.7, 2.8
├── 2.5, 2.9, 2.16 schema tests          ← models
├── 2.17-2.18 singular tests             ← 2.6
└── 2.19 generate_schema_name macro      ← No deps

Phase 3 (Airflow + Cosmos)  ← After Phase 2
├── 3.1 dbt_staging.py                   ← Phase 2
├── 3.2 dbt_marts.py                     ← Phase 2
├── 3.3 dbt_quality.py                   ← Phase 2
├── 3.4-3.6 delete old DAGs             ← 3.1, 3.2, 3.3
└── 3.7 test_dbt_dags.py                ← 3.1, 3.2, 3.3

Phase 4 (E2E Integration)  ← After Phase 1 + 3
├── 4.1 deploy.sh (modify)              ← Phase 1
├── 4.2 setup_k3s.sh                    ← No deps
├── 4.3 demo.sh                         ← 4.1
├── 4.4 airflow Terraform (modify)      ← Phase 3
└── 4.5 pyproject.toml (modify)         ← Phase 2

Phase 5 (Polish)  ← After Phase 4
├── 5.1 README.md                        ← All
├── 5.2-5.4 ADRs                        ← No deps
├── 5.5-5.6 docs updates               ← Phase 4
└── 5.7 CI final updates               ← Phase 2
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-18 | design-agent | Initial version |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_E2E_PRODUCTION.md`
