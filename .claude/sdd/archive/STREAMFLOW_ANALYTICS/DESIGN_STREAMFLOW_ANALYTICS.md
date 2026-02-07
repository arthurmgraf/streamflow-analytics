# DESIGN: StreamFlow Analytics

> Technical design for implementing a production-grade real-time streaming platform for e-commerce fraud detection on K3s

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | STREAMFLOW_ANALYTICS |
| **Date** | 2026-02-06 |
| **Author** | design-agent |
| **DEFINE** | [DEFINE_STREAMFLOW_ANALYTICS.md](./DEFINE_STREAMFLOW_ANALYTICS.md) |
| **Status** | Ready for Build |

---

## Architecture Overview

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        K3s CLUSTER (<YOUR_SERVER_IP>)                           │
│                  4 CPU │ 9.7GB RAM │ 598GB Disk │ Single-Node               │
│                  Managed by: Terraform + Terragrunt                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ ns: streamflow-kafka ──────────────────────────────────────────────────┐ │
│  │  [Strimzi Operator]                                                     │ │
│  │       │                                                                 │ │
│  │       ▼                                                                 │ │
│  │  [Kafka Broker x1]  ←── KRaft (no ZooKeeper)                          │ │
│  │       │                                                                 │ │
│  │       ├── Topic: transactions.raw (3 partitions, 7d retention)         │ │
│  │       ├── Topic: fraud.alerts     (1 partition,  30d retention)        │ │
│  │       └── Topic: metrics.realtime (1 partition,  1d retention)         │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                               │
│                              ▼                                               │
│  ┌─ ns: streamflow-processing ─────────────────────────────────────────────┐ │
│  │  [Flink K8s Operator]                                                   │ │
│  │       │                                                                 │ │
│  │       ▼                                                                 │ │
│  │  [JobManager x1] ──▶ [TaskManager x1 (2 slots)]                       │ │
│  │       │                                                                 │ │
│  │       ├── Job: transaction-processor  (Kafka → validate → Bronze)      │ │
│  │       ├── Job: fraud-detector         (Kafka → rules → alerts)         │ │
│  │       └── Job: realtime-aggregator    (Kafka → window → metrics)       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                               │
│                              ▼                                               │
│  ┌─ ns: streamflow-data ───────────────────────────────────────────────────┐ │
│  │  [CloudNativePG Operator]                                               │ │
│  │       │                                                                 │ │
│  │       ▼                                                                 │ │
│  │  [PostgreSQL 16 x1] (no replica — resource constrained)                │ │
│  │       │                                                                 │ │
│  │       ├── Schema: bronze  (raw_transactions, raw_fraud_alerts)         │ │
│  │       ├── Schema: silver  (clean_transactions, customers, stores...)   │ │
│  │       └── Schema: gold    (fact_*, dim_*, agg_*)                      │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                               │
│  ┌─ ns: streamflow-orchestration ──────────────────────────────────────────┐ │
│  │  [Airflow Helm] — LocalExecutor                                         │ │
│  │       │                                                                 │ │
│  │       ├── DAG: bronze_to_silver    (@hourly)                           │ │
│  │       ├── DAG: silver_to_gold      (@hourly, after bronze_to_silver)   │ │
│  │       ├── DAG: data_quality        (*/15 min)                          │ │
│  │       └── DAG: maintenance         (daily 03:00)                       │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌─ ns: streamflow-monitoring ─────────────────────────────────────────────┐ │
│  │  [kube-prometheus-stack Helm]                                           │ │
│  │       │                                                                 │ │
│  │       ├── Prometheus  (ServiceMonitors → Kafka, Flink, PG, Airflow)   │ │
│  │       ├── Grafana     (4 dashboards)                                   │ │
│  │       └── AlertManager (consumer lag, job failures, fraud rate)        │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

EXTERNAL:
  [Developer Machine] ──SSH──▶ [K3s Node]
  [Developer Machine] ──kubectl port-forward──▶ [Grafana, Airflow UI]
  [GitHub Actions] ──SSH/kubectl──▶ [K3s Node] (CI/CD deploy)
```

---

## Components

| Component | Purpose | Technology | Namespace | Resources (Req/Lim) |
|-----------|---------|------------|-----------|---------------------|
| Strimzi Operator | Manage Kafka lifecycle via CRDs | Strimzi 0.44+ | streamflow-kafka | 100m/200m, 128Mi/256Mi |
| Kafka Broker | Event streaming backbone (KRaft, 1 node) | Kafka 3.8+ | streamflow-kafka | 200m/500m, 512Mi/768Mi |
| Flink Operator | Manage Flink jobs via FlinkDeployment CRDs | Flink K8s Operator 1.10+ | streamflow-processing | 100m/200m, 128Mi/256Mi |
| Flink JobManager | Job coordination, checkpoint management | Flink 1.20+ | streamflow-processing | 100m/300m, 256Mi/512Mi |
| Flink TaskManager | Execute PyFlink jobs (2 task slots) | Flink 1.20+ (PyFlink) | streamflow-processing | 200m/500m, 512Mi/768Mi |
| CloudNativePG Operator | Manage PostgreSQL lifecycle | CloudNativePG 1.25+ | streamflow-data | 50m/100m, 64Mi/128Mi |
| PostgreSQL | Medallion data warehouse (Bronze/Silver/Gold) | PostgreSQL 16 | streamflow-data | 200m/500m, 256Mi/512Mi |
| Airflow Webserver | DAG visualization and management UI | Airflow 2.10+ | streamflow-orchestration | 100m/200m, 256Mi/384Mi |
| Airflow Scheduler | DAG scheduling and task execution | Airflow 2.10+ | streamflow-orchestration | 100m/200m, 256Mi/384Mi |
| Prometheus | Metrics collection and storage | Prometheus 2.x | streamflow-monitoring | 100m/200m, 256Mi/384Mi |
| Grafana | Dashboards and visualization | Grafana 11.x | streamflow-monitoring | 50m/100m, 128Mi/192Mi |

**Total Resource Budget:** ~1.3 CPU request / 2.7GB RAM request (within 4GB limit)

---

## Key Decisions

### ADR-001: Strimzi KRaft Mode (No ZooKeeper)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Kafka requires metadata management. Traditionally ZooKeeper, now KRaft (built-in).

**Choice:** Use Strimzi with KRaft mode, eliminating ZooKeeper entirely.

**Rationale:** KRaft removes the need for a separate ZooKeeper cluster, saving ~512MB RAM. ZooKeeper is deprecated in Kafka 4.0+. Strimzi 0.40+ supports KRaft GA.

**Alternatives Rejected:**
1. ZooKeeper mode — Wastes 512MB+ RAM on a resource-constrained node
2. External Kafka (Confluent Cloud) — Costs money, defeats $0 budget

**Consequences:**
- Saves ~512MB RAM and 1 pod
- Uses newer, actively developed metadata layer
- Single-broker KRaft is simpler to operate

---

### ADR-002: LocalExecutor for Airflow (Not KubernetesExecutor)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** BRAINSTORM proposed KubernetesExecutor (each task = 1 Pod), but server has only 9.7GB RAM.

**Choice:** Use LocalExecutor. Tasks run in the scheduler process.

**Rationale:** KubernetesExecutor spawns a new Pod per task, consuming ~256MB per pod. With 4 DAGs running hourly, this could spike to 1GB+ of transient pods. LocalExecutor uses zero additional pods — tasks run inside the scheduler.

**Alternatives Rejected:**
1. KubernetesExecutor — Too resource-hungry for single-node K3s with 4GB budget
2. CeleryExecutor — Requires Redis/RabbitMQ (more pods, more RAM)

**Consequences:**
- No task isolation (acceptable for portfolio project)
- No parallelism beyond scheduler capacity (acceptable — DAGs are sequential)
- Saves ~512MB-1GB of transient pod resources

---

### ADR-003: Single PostgreSQL Instance (No Replica)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** CloudNativePG supports primary + N replicas. BRAINSTORM proposed primary + 1 replica.

**Choice:** Single instance (instances: 1). No read replica.

**Rationale:** Each PG replica consumes ~256-512MB RAM. With our 4GB budget, a replica would consume 10-15% of total allocation. For a portfolio project, HA is not critical — data can be regenerated.

**Alternatives Rejected:**
1. Primary + 1 replica — 256-512MB extra RAM for HA we don't need
2. External managed PostgreSQL — Costs money

**Consequences:**
- No HA for PostgreSQL (acceptable — portfolio, not production)
- Single point of failure for data (mitigated by regeneratable data)
- CloudNativePG still manages automated backups to local storage

---

### ADR-004: Schemas Over Databases for Medallion Layers

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** BRAINSTORM proposed 3 separate databases (bronze_db, silver_db, gold_db). But cross-database queries in PostgreSQL require dblink/FDW.

**Choice:** Single database `streamflow` with 3 schemas: `bronze`, `silver`, `gold`.

**Rationale:** PostgreSQL schemas provide logical separation without the complexity of cross-database joins. Airflow DAGs can transform data within a single connection. Simpler connection management, no FDW overhead.

**Alternatives Rejected:**
1. 3 databases — Cross-DB queries need dblink/FDW, complex connection management
2. Single schema with prefixes — Poor separation, no access control granularity

**Consequences:**
- All layers accessible in single connection (simpler DAGs)
- Schema-level grants possible (future improvement)
- Standard pattern for data warehouses (Snowflake, BigQuery use similar approach)

---

### ADR-005: Terraform Kubernetes + Helm Providers (Not kubectl apply)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** K8s resources can be managed by kubectl, Helm, or Terraform.

**Choice:** Terraform with `kubernetes` and `helm` providers, orchestrated by Terragrunt.

**Rationale:** Terraform provides state management, plan/apply workflow, and declarative infrastructure. Combined with Terragrunt for DRY configurations across modules. This is the pattern used by platform engineering teams at scale.

**Alternatives Rejected:**
1. `kubectl apply` scripts — No state, no rollback, error-prone
2. Helm only — No cross-resource dependencies, no state for non-Helm resources
3. Pulumi — Less industry adoption for data engineering roles

**Consequences:**
- All infrastructure is code-reviewable
- `terragrunt run-all apply` provisions everything from scratch
- State stored locally (acceptable for single developer)

---

### ADR-006: Python Monorepo Structure (Not Microservices)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Flink jobs, Airflow DAGs, generators, and models could be separate packages/repos.

**Choice:** Single `src/` directory with subpackages. Single `pyproject.toml`. Shared models via `src/models/`.

**Rationale:** For a portfolio project, a monorepo is simpler to navigate, test, and showcase. Shared Pydantic models between Flink jobs and generators ensure schema consistency. Single CI pipeline covers everything.

**Alternatives Rejected:**
1. Separate repos per component — Overhead without benefit for single developer
2. Separate pyproject.toml per package — Complex dependency management

**Consequences:**
- All code in one repo (easy to clone, review, star)
- Shared models prevent schema drift
- Single `pytest` run covers everything

---

### ADR-007: Terraform Local Backend (Not Remote State)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Terraform state can be stored locally or remotely (S3, GCS, Consul).

**Choice:** Local backend. State files stored in `.terraform/` directories (gitignored).

**Rationale:** Single developer project. No team collaboration on Terraform. Remote state requires a cloud storage bucket (costs money or requires additional setup). Local state is sufficient.

**Alternatives Rejected:**
1. S3/GCS remote state — Requires cloud account and costs
2. Kubernetes backend — Experimental, not production-stable
3. GitLab/GitHub backend — Requires CI integration complexity

**Consequences:**
- State lives on developer machine only
- `terraform.tfstate` files are gitignored (security)
- If state is lost, `terraform import` or recreate (acceptable)

---

## Data Flow (Detailed)

```text
STREAMING PATH (Real-time, < 30s latency)
═══════════════════════════════════════════════════════════════════

1. DATA GENERATION
   [scripts/generate_events.py]
   │  ├── Loads Kaggle dataset statistics (distributions)
   │  ├── Generates realistic Transaction events (Pydantic validated)
   │  ├── Injects fraud patterns (configurable rate, default 2%)
   │  └── Produces to Kafka topic: transactions.raw
   │
   ▼
2. KAFKA INGESTION
   [Kafka Broker — transactions.raw topic]
   │  ├── 3 partitions (keyed by customer_id for ordering)
   │  ├── 7-day retention
   │  └── Consumer groups: flink-processor, flink-fraud
   │
   ▼
3. FLINK PROCESSING (3 parallel jobs)
   │
   ├── [transaction-processor] ─────────────────────────────────┐
   │   ├── Kafka Source (transactions.raw)                      │
   │   ├── Deserialize JSON → Transaction model                 │
   │   ├── Schema validation (reject malformed)                 │
   │   ├── Add processing metadata (ingested_at, schema_ver)    │
   │   └── JDBC Sink → bronze.raw_transactions                  │
   │                                                            │
   ├── [fraud-detector] ────────────────────────────────────────┤
   │   ├── Kafka Source (transactions.raw)                      │
   │   ├── Keyed by customer_id                                 │
   │   ├── ProcessFunction with ValueState:                     │
   │   │   ├── FR-001: High Value (keyed avg comparison)        │
   │   │   ├── FR-002: Velocity (count window 10min)            │
   │   │   ├── FR-003: Geographic (haversine + time delta)      │
   │   │   ├── FR-004: Time Anomaly (hour distribution)         │
   │   │   └── FR-005: Blacklist (broadcast state)              │
   │   ├── Score combination (weighted average)                 │
   │   ├── If score > 0.7 → Kafka Sink: fraud.alerts            │
   │   └── JDBC Sink → bronze.raw_fraud_alerts                  │
   │                                                            │
   └── [realtime-aggregator] ───────────────────────────────────┘
       ├── Kafka Source (transactions.raw)
       ├── Tumbling Windows: 1min, 5min, 1h
       ├── Aggregate: count, sum, avg per store_id
       └── Kafka Sink → metrics.realtime


BATCH PATH (Airflow, hourly)
═══════════════════════════════════════════════════════════════════

4. BRONZE → SILVER (DAG: bronze_to_silver, @hourly)
   │  ├── Read new rows from bronze.raw_transactions (incremental)
   │  ├── SQL Transform:
   │  │   ├── Parse JSONB → typed columns
   │  │   ├── Validate: nulls, ranges, types
   │  │   ├── Deduplicate by transaction_id
   │  │   ├── Enrich with customer/store reference data
   │  │   └── Compute fraud_score from raw_fraud_alerts
   │  └── Insert into silver.clean_transactions
   │
   ▼
5. SILVER → GOLD (DAG: silver_to_gold, @hourly)
   │  ├── Upsert dimensions: dim_customer, dim_store, dim_product, dim_date
   │  ├── Build fact_transactions (with surrogate keys)
   │  ├── Build fact_fraud_alerts
   │  ├── Compute agg_hourly_sales
   │  └── Compute agg_daily_fraud
   │
   ▼
6. DATA QUALITY (DAG: data_quality, every 15min)
   │  ├── Check: null rates per column (threshold: < 5%)
   │  ├── Check: duplicate transaction_ids (threshold: 0%)
   │  ├── Check: freshness (last record < 30 min old)
   │  ├── Check: referential integrity (FKs valid)
   │  └── Log results to quality_check_results table
   │
   ▼
7. GRAFANA DASHBOARDS
   ├── Pipeline Overview: throughput, latency, error rates
   ├── Kafka Metrics: consumer lag, broker health, topic sizes
   ├── Flink Processing: job status, checkpoints, backpressure
   └── Fraud Monitoring: alert rate, top rules, trends
```

---

## SQL Schema Design

### Bronze Schema

```sql
-- sql/migrations/001_create_bronze_schema.sql

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

    -- Deduplication constraint
    UNIQUE (kafka_topic, kafka_partition, kafka_offset)
);

-- Partition by month for efficient pruning
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
```

### Silver Schema

```sql
-- sql/migrations/002_create_silver_schema.sql

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

    -- Constraints
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
```

### Gold Schema

```sql
-- sql/migrations/003_create_gold_schema.sql

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
```

---

## Integration Points

| System A | System B | Integration | Protocol | Auth |
|----------|----------|-------------|----------|------|
| Generator | Kafka | Kafka Producer (confluent-kafka-python) | TCP/9092 | PLAINTEXT (internal K8s) |
| Kafka | Flink | Kafka Consumer (FlinkKafkaConsumer) | TCP/9092 | PLAINTEXT |
| Flink | PostgreSQL | JDBC Sink | TCP/5432 | User/password (K8s Secret) |
| Airflow | PostgreSQL | PostgresHook | TCP/5432 | User/password (K8s Secret) |
| Prometheus | Kafka | JMX Exporter → ServiceMonitor | HTTP/9404 | None |
| Prometheus | Flink | Flink Metrics Reporter → ServiceMonitor | HTTP/9249 | None |
| Prometheus | PostgreSQL | postgres_exporter → ServiceMonitor | HTTP/9187 | None |
| Grafana | Prometheus | PromQL queries | HTTP/9090 | None |
| Developer | Grafana | kubectl port-forward | HTTP/3000 | admin/admin |
| Developer | Airflow | kubectl port-forward | HTTP/8080 | admin/admin |
| GitHub Actions | K3s | SSH + kubectl | TCP/22 + TCP/6443 | SSH key + kubeconfig |

---

## Code Patterns

### Pattern 1: Pydantic Model (Transaction Event)

```python
# src/models/transaction.py
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator

class Transaction(BaseModel):
    """Transaction event from e-commerce system."""
    transaction_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    store_id: str = Field(..., min_length=1)
    product_id: str | None = None
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")
    payment_method: str | None = None
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    timestamp: datetime

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: object) -> Decimal:
        return Decimal(str(v))
```

### Pattern 2: PyFlink Job (Kafka → ProcessFunction → JDBC)

```python
# src/flink_jobs/transaction_processor.py
import json
import logging
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaOffsetsInitializer,
    KafkaSource,
)
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy
from pyflink.datastream.connectors.jdbc import (
    JdbcConnectionOptions,
    JdbcExecutionOptions,
    JdbcSink,
)

logger = logging.getLogger(__name__)

def build_pipeline(env: StreamExecutionEnvironment, config: dict) -> None:
    """Build the transaction processing pipeline."""
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(config["kafka"]["bootstrap_servers"])
        .set_topics(config["kafka"]["topics"]["transactions"])
        .set_group_id("flink-transaction-processor")
        .set_starting_offsets(KafkaOffsetsInitializer.latest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    ds = env.from_source(
        kafka_source,
        WatermarkStrategy.for_monotonous_timestamps(),
        "kafka-transactions",
    )

    # Parse, validate, transform
    validated = ds.map(parse_and_validate).filter(lambda x: x is not None)

    # Sink to PostgreSQL Bronze
    jdbc_sink = JdbcSink.sink(
        "INSERT INTO bronze.raw_transactions "
        "(kafka_topic, kafka_partition, kafka_offset, event_timestamp, raw_payload) "
        "VALUES (?, ?, ?, ?, ?::jsonb) "
        "ON CONFLICT (kafka_topic, kafka_partition, kafka_offset) DO NOTHING",
        type_info=...,  # Row type info
        jdbc_connection_options=(
            JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
            .with_url(config["postgres"]["jdbc_url"])
            .with_driver_name("org.postgresql.Driver")
            .with_user_name(config["postgres"]["user"])
            .with_password(config["postgres"]["password"])
            .build()
        ),
        jdbc_execution_options=(
            JdbcExecutionOptions.builder()
            .with_batch_interval_ms(1000)
            .with_batch_size(100)
            .build()
        ),
    )

    validated.add_sink(jdbc_sink)
```

### Pattern 3: PyFlink Fraud Rule (Keyed State)

```python
# src/flink_jobs/fraud_detector.py — High Value Rule
from pyflink.datastream import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor
from pyflink.common.typeinfo import Types

class HighValueRule(KeyedProcessFunction):
    """FR-001: Detect transactions > 3x customer average."""

    def __init__(self, multiplier: float = 3.0):
        self.multiplier = multiplier
        self.avg_state = None
        self.count_state = None

    def open(self, ctx: RuntimeContext) -> None:
        self.avg_state = ctx.get_state(
            ValueStateDescriptor("customer_avg", Types.DOUBLE())
        )
        self.count_state = ctx.get_state(
            ValueStateDescriptor("customer_count", Types.LONG())
        )

    def process_element(self, txn, ctx):
        current_avg = self.avg_state.value() or 0.0
        count = self.count_state.value() or 0

        # Update running average
        count += 1
        new_avg = current_avg + (txn.amount - current_avg) / count

        # Check rule (only after 5+ transactions for statistical significance)
        score = 0.0
        if count >= 5 and txn.amount > new_avg * self.multiplier:
            score = min(1.0, txn.amount / (new_avg * self.multiplier))

        # Persist state
        self.avg_state.update(new_avg)
        self.count_state.update(count)

        yield {**txn, "high_value_score": score}
```

### Pattern 4: Airflow DAG (Bronze → Silver)

```python
# src/dags/bronze_to_silver.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="bronze_to_silver",
    default_args=default_args,
    description="Transform raw Bronze data to cleaned Silver layer",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "medallion", "silver"],
) as dag:
    transform_transactions = PostgresOperator(
        task_id="transform_transactions",
        postgres_conn_id="streamflow_postgres",
        sql="sql/transforms/bronze_to_silver.sql",
    )

    update_customer_stats = PostgresOperator(
        task_id="update_customer_stats",
        postgres_conn_id="streamflow_postgres",
        sql="sql/transforms/update_customer_stats.sql",
    )

    transform_transactions >> update_customer_stats
```

### Pattern 5: Terraform Module (Helm Release)

```hcl
# infra/modules/strimzi-kafka/main.tf

resource "helm_release" "strimzi_operator" {
  name             = "strimzi"
  repository       = "https://strimzi.io/charts/"
  chart            = "strimzi-kafka-operator"
  version          = var.strimzi_chart_version
  namespace        = var.namespace
  create_namespace = true

  set {
    name  = "resources.requests.memory"
    value = "128Mi"
  }
  set {
    name  = "resources.requests.cpu"
    value = "100m"
  }
  set {
    name  = "resources.limits.memory"
    value = "256Mi"
  }
  set {
    name  = "resources.limits.cpu"
    value = "200m"
  }
}

resource "kubectl_manifest" "kafka_cluster" {
  depends_on = [helm_release.strimzi_operator]
  yaml_body  = templatefile("${path.module}/templates/kafka-cluster.yaml.tpl", {
    name              = var.kafka_cluster_name
    namespace         = var.namespace
    replicas          = var.kafka_replicas
    storage_size      = var.kafka_storage_size
    memory_request    = var.kafka_memory_request
    memory_limit      = var.kafka_memory_limit
    cpu_request       = var.kafka_cpu_request
    cpu_limit         = var.kafka_cpu_limit
  })
}
```

### Pattern 6: Terragrunt Root Config

```hcl
# infra/environments/terragrunt.hcl (root)

locals {
  env = basename(get_terragrunt_dir())
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
    terraform {
      required_version = ">= 1.7"
      required_providers {
        kubernetes = {
          source  = "hashicorp/kubernetes"
          version = "~> 2.35"
        }
        helm = {
          source  = "hashicorp/helm"
          version = "~> 2.17"
        }
        kubectl = {
          source  = "alekc/kubectl"
          version = "~> 2.1"
        }
      }
    }

    provider "kubernetes" {
      config_path = "~/.kube/config"
    }

    provider "helm" {
      kubernetes {
        config_path = "~/.kube/config"
      }
    }

    provider "kubectl" {
      config_path = "~/.kube/config"
    }
  EOF
}
```

### Pattern 7: Configuration Structure

```yaml
# config/default.yaml
project:
  name: streamflow-analytics
  version: 0.1.0

kafka:
  bootstrap_servers: "streamflow-kafka-bootstrap.streamflow-kafka.svc.cluster.local:9092"
  topics:
    transactions: "transactions.raw"
    fraud_alerts: "fraud.alerts"
    metrics: "metrics.realtime"

postgres:
  host: "streamflow-pg-rw.streamflow-data.svc.cluster.local"
  port: 5432
  database: "streamflow"
  user: "streamflow"

flink:
  checkpoint_interval_ms: 60000
  parallelism: 2

fraud_rules:
  high_value:
    enabled: true
    multiplier: 3.0
    min_transactions: 5
  velocity:
    enabled: true
    max_count: 5
    window_minutes: 10
  geographic:
    enabled: true
    max_distance_km: 500
    max_time_hours: 1
  time_anomaly:
    enabled: true
    std_dev_threshold: 2.0
  blacklist:
    enabled: true
    refresh_interval_seconds: 300

generator:
  events_per_second: 100
  fraud_rate: 0.02
  num_customers: 1000
  num_stores: 10
  num_products: 50
```

---

## File Manifest

### Phase 1: Foundation (18 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 1 | `pyproject.toml` | Modify | Project config: deps, ruff, mypy, pytest | @python-developer |
| 2 | `.pre-commit-config.yaml` | Create | Pre-commit hooks: ruff, mypy, trailing whitespace | @python-developer |
| 3 | `Makefile` | Create | Dev commands: lint, test, typecheck, format | @python-developer |
| 4 | `src/__init__.py` | Modify | Package init with version | @python-developer |
| 5 | `src/models/__init__.py` | Create | Models package init | @python-developer |
| 6 | `src/models/transaction.py` | Create | Transaction Pydantic model | @python-developer |
| 7 | `src/models/customer.py` | Create | Customer Pydantic model | @python-developer |
| 8 | `src/models/store.py` | Create | Store Pydantic model | @python-developer |
| 9 | `src/models/fraud_alert.py` | Create | FraudAlert Pydantic model | @python-developer |
| 10 | `src/utils/__init__.py` | Create | Utils package init | @python-developer |
| 11 | `src/utils/config.py` | Create | YAML config loader | @python-developer |
| 12 | `src/utils/logging.py` | Create | Structured JSON logging setup | @python-developer |
| 13 | `src/utils/db.py` | Create | PostgreSQL connection helper | @python-developer |
| 14 | `config/default.yaml` | Create | Default application config | @python-developer |
| 15 | `config/dev.yaml` | Create | Dev environment overrides | @python-developer |
| 16 | `config/fraud_rules.yaml` | Create | Fraud detection rules config | @python-developer |
| 17 | `tests/unit/test_models.py` | Create | Pydantic model tests | @test-generator |
| 18 | `tests/unit/test_config.py` | Create | Config loading tests | @test-generator |

### Phase 2: Infrastructure (22 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 19 | `infra/modules/namespaces/main.tf` | Create | K8s namespace creation | @infra-deployer |
| 20 | `infra/modules/namespaces/variables.tf` | Create | Namespace variables | @infra-deployer |
| 21 | `infra/modules/strimzi-kafka/main.tf` | Create | Strimzi operator + Kafka cluster | @infra-deployer |
| 22 | `infra/modules/strimzi-kafka/variables.tf` | Create | Kafka variables | @infra-deployer |
| 23 | `infra/modules/strimzi-kafka/outputs.tf` | Create | Kafka outputs (bootstrap) | @infra-deployer |
| 24 | `infra/modules/strimzi-kafka/templates/kafka-cluster.yaml.tpl` | Create | Strimzi Kafka CRD template | @infra-deployer |
| 25 | `infra/modules/flink-operator/main.tf` | Create | Flink K8s Operator | @infra-deployer |
| 26 | `infra/modules/flink-operator/variables.tf` | Create | Flink variables | @infra-deployer |
| 27 | `infra/modules/cloudnativepg/main.tf` | Create | CNPG operator + PG cluster | @infra-deployer |
| 28 | `infra/modules/cloudnativepg/variables.tf` | Create | PG variables | @infra-deployer |
| 29 | `infra/modules/cloudnativepg/outputs.tf` | Create | PG outputs (connection) | @infra-deployer |
| 30 | `infra/modules/cloudnativepg/templates/pg-cluster.yaml.tpl` | Create | CNPG Cluster CRD template | @infra-deployer |
| 31 | `infra/modules/airflow/main.tf` | Create | Airflow Helm release | @infra-deployer |
| 32 | `infra/modules/airflow/variables.tf` | Create | Airflow variables | @infra-deployer |
| 33 | `infra/modules/airflow/values.yaml` | Create | Airflow Helm values override | @infra-deployer |
| 34 | `infra/modules/monitoring/main.tf` | Create | kube-prometheus-stack | @infra-deployer |
| 35 | `infra/modules/monitoring/variables.tf` | Create | Monitoring variables | @infra-deployer |
| 36 | `infra/environments/terragrunt.hcl` | Create | Root Terragrunt config | @infra-deployer |
| 37 | `infra/environments/dev/terragrunt.hcl` | Create | Dev env base | @infra-deployer |
| 38 | `infra/environments/dev/namespaces/terragrunt.hcl` | Create | Dev namespaces | @infra-deployer |
| 39 | `infra/environments/dev/kafka/terragrunt.hcl` | Create | Dev Kafka config | @infra-deployer |
| 40 | `infra/environments/dev/flink/terragrunt.hcl` | Create | Dev Flink config | @infra-deployer |
| 41 | `infra/environments/dev/postgresql/terragrunt.hcl` | Create | Dev PostgreSQL config | @infra-deployer |
| 42 | `infra/environments/dev/airflow/terragrunt.hcl` | Create | Dev Airflow config | @infra-deployer |
| 43 | `infra/environments/dev/monitoring/terragrunt.hcl` | Create | Dev monitoring config | @infra-deployer |

### Phase 3: Streaming Core (10 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 44 | `src/flink_jobs/__init__.py` | Create | Flink jobs package | @python-developer |
| 45 | `src/flink_jobs/common/__init__.py` | Create | Common Flink utilities | @python-developer |
| 46 | `src/flink_jobs/common/serialization.py` | Create | Kafka SerDe for Flink | @python-developer |
| 47 | `src/flink_jobs/common/schemas.py` | Create | Flink type mappings | @python-developer |
| 48 | `src/flink_jobs/transaction_processor.py` | Create | Kafka → validate → Bronze | @python-developer |
| 49 | `k8s/flink/transaction-processor.yaml` | Create | FlinkDeployment CRD | @infra-deployer |
| 50 | `k8s/kafka/kafka-topics.yaml` | Create | Strimzi KafkaTopic CRDs | @infra-deployer |
| 51 | `k8s/kafka/kafka-users.yaml` | Create | Strimzi KafkaUser CRDs | @infra-deployer |
| 52 | `tests/unit/test_transaction_processor.py` | Create | Processor unit tests | @test-generator |
| 53 | `tests/unit/test_serialization.py` | Create | SerDe tests | @test-generator |

### Phase 4: Fraud Detection (6 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 54 | `src/flink_jobs/fraud_detector.py` | Create | 5 fraud rules in PyFlink | @python-developer |
| 55 | `src/flink_jobs/common/state.py` | Create | State management helpers | @python-developer |
| 56 | `k8s/flink/fraud-detector.yaml` | Create | FlinkDeployment CRD | @infra-deployer |
| 57 | `tests/unit/test_fraud_detector.py` | Create | Per-rule unit tests | @test-generator |
| 58 | `tests/unit/test_fraud_rules.py` | Create | Rule logic edge cases | @test-generator |
| 59 | `tests/integration/test_fraud_flow.py` | Create | End-to-end fraud flow | @test-generator |

### Phase 5: Batch Processing (10 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 60 | `sql/migrations/001_create_bronze_schema.sql` | Create | Bronze layer DDL | @medallion-architect |
| 61 | `sql/migrations/002_create_silver_schema.sql` | Create | Silver layer DDL | @medallion-architect |
| 62 | `sql/migrations/003_create_gold_schema.sql` | Create | Gold layer DDL | @medallion-architect |
| 63 | `sql/migrations/004_create_indexes.sql` | Create | Performance indexes | @medallion-architect |
| 64 | `sql/transforms/bronze_to_silver.sql` | Create | Bronze→Silver transform | @medallion-architect |
| 65 | `sql/transforms/silver_to_gold.sql` | Create | Silver→Gold transform | @medallion-architect |
| 66 | `sql/quality/quality_checks.sql` | Create | Data quality queries | @medallion-architect |
| 67 | `src/dags/bronze_to_silver.py` | Create | Airflow DAG | @python-developer |
| 68 | `src/dags/silver_to_gold.py` | Create | Airflow DAG | @python-developer |
| 69 | `src/dags/data_quality.py` | Create | Airflow DAG | @python-developer |
| 70 | `src/dags/maintenance.py` | Create | Airflow DAG | @python-developer |

### Phase 6: Data Generation (8 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 71 | `src/generators/__init__.py` | Create | Generators package | @python-developer |
| 72 | `src/generators/transaction_generator.py` | Create | Realistic transaction events | @python-developer |
| 73 | `src/generators/customer_generator.py` | Create | Customer profiles | @python-developer |
| 74 | `src/generators/store_generator.py` | Create | Store data | @python-developer |
| 75 | `src/generators/fraud_patterns.py` | Create | Fraud injection logic | @python-developer |
| 76 | `src/generators/kafka_producer.py` | Create | Kafka producer wrapper | @python-developer |
| 77 | `scripts/generate_events.py` | Create | CLI for generating events | @python-developer |
| 78 | `scripts/seed_data.py` | Create | Seed reference data | @python-developer |
| 79 | `tests/unit/test_generators.py` | Create | Generator tests | @test-generator |

### Phase 7: Monitoring (7 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 80 | `k8s/monitoring/grafana-dashboards/pipeline-overview.json` | Create | Pipeline dashboard | @pipeline-architect |
| 81 | `k8s/monitoring/grafana-dashboards/kafka-metrics.json` | Create | Kafka dashboard | @pipeline-architect |
| 82 | `k8s/monitoring/grafana-dashboards/flink-processing.json` | Create | Flink dashboard | @pipeline-architect |
| 83 | `k8s/monitoring/grafana-dashboards/fraud-monitoring.json` | Create | Fraud dashboard | @pipeline-architect |
| 84 | `k8s/monitoring/alerting-rules.yaml` | Create | AlertManager rules | @pipeline-architect |
| 85 | `k8s/monitoring/service-monitors.yaml` | Create | Prometheus ServiceMonitors | @pipeline-architect |
| 86 | `scripts/run_migrations.py` | Create | SQL migration runner | @python-developer |

### Phase 8: CI/CD + Docs (11 files)

| # | File | Action | Purpose | Agent |
|---|------|--------|---------|-------|
| 87 | `.github/workflows/ci.yaml` | Create | CI: lint + test + typecheck | @ci-cd-specialist |
| 88 | `.github/workflows/deploy.yaml` | Create | CD: deploy to K3s | @ci-cd-specialist |
| 89 | `README.md` | Modify | Professional README with demos | @code-documenter |
| 90 | `ARCHITECTURE.md` | Create | ADRs + architecture details | @code-documenter |
| 91 | `docs/SETUP_GUIDE.md` | Create | Step-by-step setup | @code-documenter |
| 92 | `docs/FRAUD_DETECTION.md` | Create | Fraud rules documentation | @code-documenter |
| 93 | `docs/RUNBOOK.md` | Create | Operations runbook | @code-documenter |
| 94 | `scripts/verify_pipeline.py` | Create | E2E pipeline verification | @python-developer |
| 95 | `scripts/setup.sh` | Create | Initial cluster bootstrap | @infra-deployer |
| 96 | `tests/e2e/test_full_pipeline.py` | Create | Full E2E test | @test-generator |
| 97 | `k8s/flink/realtime-aggregator.yaml` | Create | FlinkDeployment CRD | @infra-deployer |

**Total Files: 97** (76 Create + 3 Modify + 18 package __init__.py implicit)

---

## Agent Assignment Rationale

| Agent | Files Assigned | Why This Agent |
|-------|----------------|----------------|
| @python-developer | 1-16, 44-48, 54-55, 67-78, 86, 94 | Python code specialist: Pydantic, PyFlink, Airflow, generators |
| @infra-deployer | 19-43, 49-51, 56, 95, 97 | Terraform/Terragrunt/K8s manifests specialist |
| @test-generator | 17-18, 52-53, 57-59, 79, 96 | pytest test automation specialist |
| @medallion-architect | 60-66 | SQL schema design for Bronze/Silver/Gold layers |
| @pipeline-architect | 80-85 | Monitoring configs: Grafana dashboards, Prometheus rules |
| @ci-cd-specialist | 87-88 | GitHub Actions CI/CD pipelines |
| @code-documenter | 89-93 | Documentation: README, Architecture, Guides |

---

## Testing Strategy

| Test Type | Scope | Files | Tools | Coverage Goal | Runs Without K8s? |
|-----------|-------|-------|-------|---------------|-------------------|
| **Unit** | Pydantic models, fraud rules, generators, transforms, config | `tests/unit/test_*.py` | pytest + pytest-cov | 80%+ | Yes |
| **Integration** | Fraud flow (mocked Kafka/PG), DAG parsing | `tests/integration/test_*.py` | pytest + testcontainers | Key paths | Needs Docker |
| **E2E** | Full pipeline (Generator → Kafka → Flink → PG → Grafana) | `tests/e2e/test_full_pipeline.py` | pytest + K8s port-forward | Happy path | Needs K8s |
| **Lint** | All Python files | N/A | ruff check . | Zero warnings | Yes |
| **Type Check** | All Python files | N/A | mypy src/ | Zero errors | Yes |
| **SQL** | Migration syntax, transform logic | Embedded in unit tests | pytest + psycopg2 (mock) | Key queries | Yes |

### Unit Test Patterns

```python
# tests/unit/test_fraud_detector.py
import pytest
from src.flink_jobs.fraud_detector import HighValueRule

class TestHighValueRule:
    """Tests for FR-001: High Value detection."""

    def test_normal_transaction_no_alert(self):
        """Transaction within normal range produces score 0."""
        rule = HighValueRule(multiplier=3.0)
        # Mock state with avg=100, count=10
        result = rule.evaluate(amount=200, customer_avg=100, count=10)
        assert result.score == 0.0

    def test_high_value_triggers_alert(self):
        """Transaction > 3x average produces positive score."""
        rule = HighValueRule(multiplier=3.0)
        result = rule.evaluate(amount=500, customer_avg=100, count=10)
        assert result.score > 0.0

    def test_insufficient_history_no_alert(self):
        """< 5 transactions — insufficient data, no alert."""
        rule = HighValueRule(multiplier=3.0)
        result = rule.evaluate(amount=9999, customer_avg=10, count=3)
        assert result.score == 0.0
```

---

## Error Handling

| Error Type | Where | Strategy | Retry? | Alert? |
|------------|-------|----------|--------|--------|
| Kafka unavailable | Flink jobs | Flink auto-retries with backoff | Yes (built-in) | Yes (job restart count > 3) |
| PostgreSQL connection failure | Flink JDBC sink | Batch retry with exponential backoff | Yes (3 retries) | Yes (consecutive failures) |
| Malformed JSON event | transaction_processor | Log error, skip event, increment metric | No | Yes (error rate > 5%) |
| Schema validation failure | transaction_processor | Route to dead-letter topic (future) / skip + log | No | Yes (error rate > 5%) |
| DAG task failure | Airflow | Retry 2x with 2min delay, then mark failed | Yes (2 retries) | Yes (DAG SLA miss) |
| OOM on TaskManager | Flink | K8s restarts pod, Flink resumes from checkpoint | Yes (automatic) | Yes (restart count) |
| Disk full on PostgreSQL | CloudNativePG | Maintenance DAG prunes old data | N/A (prevention) | Yes (PVC > 80%) |

---

## Observability

| Aspect | Implementation |
|--------|----------------|
| **Logging** | Structured JSON via Python `logging` with `json-log-formatter`. All Flink jobs, DAGs, generators log to stdout (K8s collects). Fields: timestamp, level, component, message, extra. |
| **Metrics** | Prometheus scrapes: Kafka (JMX exporter), Flink (prometheus reporter), PostgreSQL (postgres_exporter), Airflow (StatsD → Prometheus). Custom metrics via Flink counters. |
| **Dashboards** | 4 Grafana dashboards provisioned via ConfigMap: Pipeline Overview, Kafka Metrics, Flink Processing, Fraud Monitoring. |
| **Alerting** | AlertManager rules: consumer lag > 10k (warning), Flink job not RUNNING (critical), fraud rate > 5%/h (warning), DAG SLA miss (warning). |

---

## Security Considerations

- **No sensitive data in git:** `.env.local` and `terraform.tfstate` are gitignored
- **K8s Secrets for passwords:** PostgreSQL credentials stored as K8s Secret, referenced in Helm values
- **PLAINTEXT Kafka auth:** Acceptable for internal K8s communication (no external access)
- **No Ingress:** All UIs accessed via `kubectl port-forward` only
- **Minimal RBAC:** Single namespace admin per streamflow-* namespace (future improvement)
- **No PII in logs:** Transaction amounts logged, but customer names/emails are not

---

## Configuration

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `kafka.bootstrap_servers` | string | `streamflow-kafka-bootstrap...` | Kafka cluster internal address |
| `postgres.host` | string | `streamflow-pg-rw...` | PostgreSQL read-write service |
| `postgres.database` | string | `streamflow` | Database name |
| `flink.checkpoint_interval_ms` | int | `60000` | Flink checkpoint interval |
| `flink.parallelism` | int | `2` | Default parallelism |
| `fraud_rules.high_value.multiplier` | float | `3.0` | High value threshold multiplier |
| `fraud_rules.velocity.max_count` | int | `5` | Max transactions in window |
| `fraud_rules.velocity.window_minutes` | int | `10` | Velocity window size |
| `generator.events_per_second` | int | `100` | Generator throughput |
| `generator.fraud_rate` | float | `0.02` | Percentage of fraudulent events |

---

## Deployment Sequence

```text
terragrunt run-all apply executes in this order (respects dependencies):

1. namespaces          ← No dependencies (creates 5 namespaces)
   │
   ├──▶ 2. kafka       ← Depends on: namespaces
   ├──▶ 3. postgresql   ← Depends on: namespaces
   ├──▶ 4. monitoring   ← Depends on: namespaces
   │
   ├──▶ 5. flink        ← Depends on: namespaces, kafka (needs bootstrap addr)
   │
   └──▶ 6. airflow      ← Depends on: namespaces, postgresql (needs connection)

Post-Terraform (manual/CI):
   7. kubectl apply -f k8s/kafka/kafka-topics.yaml
   8. python scripts/run_migrations.py
   9. python scripts/seed_data.py
   10. kubectl apply -f k8s/flink/transaction-processor.yaml
   11. kubectl apply -f k8s/flink/fraud-detector.yaml
   12. kubectl apply -f k8s/flink/realtime-aggregator.yaml
   13. python scripts/generate_events.py --events 1000
```

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-06 | design-agent | Initial version from DEFINE_STREAMFLOW_ANALYTICS.md |

---

## Next Step

**Ready for:** `/build .claude/sdd/features/DESIGN_STREAMFLOW_ANALYTICS.md`
