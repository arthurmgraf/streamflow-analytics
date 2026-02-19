# Architecture — StreamFlow Analytics

> Detailed architecture documentation, ADRs, and data flow for the StreamFlow Analytics platform.

---

## System Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        K3s CLUSTER (<YOUR_SERVER_IP>)                           │
│                  4 CPU │ 9.7GB RAM │ 598GB Disk │ Single-Node               │
│                  OS: Ubuntu 22.04 │ K3s v1.34                                │
│                  Managed by: Terraform + Terragrunt                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ ns: streamflow-kafka ──────────────────────────────────────────────────┐ │
│  │  [Strimzi Operator] → [Kafka Broker x1 (KRaft)]                       │ │
│  │  Topics: transactions.raw (3p, 7d) │ fraud.alerts (1p, 30d)           │ │
│  │          metrics.realtime (1p, 1d)                                     │ │
│  │  Resources: 300m/700m CPU, 640Mi/1024Mi RAM                           │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                               │
│  ┌─ ns: streamflow-processing ─────────────────────────────────────────────┐ │
│  │  [Flink K8s Operator] → [JobManager x1] → [TaskManager x1 (2 slots)] │ │
│  │  Jobs: transaction-processor │ fraud-detector │ realtime-aggregator    │ │
│  │  Resources: 400m/1000m CPU, 896Mi/1536Mi RAM                          │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                               │
│  ┌─ ns: streamflow-data ──────────────────────────────────────────────────┐  │
│  │  [CloudNativePG Operator] → [PostgreSQL 16 x1 (no replica)]           │  │
│  │  Schemas: bronze │ silver │ gold                                       │  │
│  │  Resources: 250m/600m CPU, 320Mi/640Mi RAM                            │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│  ┌─ ns: streamflow-orchestration ──────────────────────────────────────────┐ │
│  │  [Airflow Helm — LocalExecutor]                                        │ │
│  │  DAGs: dbt_staging │ dbt_marts │ dbt_quality │ maintenance              │ │
│  │  Resources: 200m/400m CPU, 512Mi/768Mi RAM                            │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                              │                                               │
│  ┌─ ns: streamflow-monitoring ─────────────────────────────────────────────┐ │
│  │  [kube-prometheus-stack Helm]                                          │ │
│  │  Prometheus + Grafana (4 dashboards) + AlertManager (9 rules)         │ │
│  │  Resources: 150m/300m CPU, 384Mi/576Mi RAM                            │ │
│  └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  TOTAL: ~1.3 CPU request / ~2.7GB RAM request (within 4GB budget)           │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

| Component | Technology | Namespace | CPU Req/Lim | RAM Req/Lim |
|-----------|-----------|-----------|-------------|-------------|
| Strimzi Operator | Strimzi 0.44+ | streamflow-kafka | 100m/200m | 128Mi/256Mi |
| Kafka Broker (KRaft) | Kafka 3.8+ | streamflow-kafka | 200m/500m | 512Mi/768Mi |
| Flink Operator | Flink K8s Op 1.10+ | streamflow-processing | 100m/200m | 128Mi/256Mi |
| Flink JobManager | Flink 1.20+ | streamflow-processing | 100m/300m | 256Mi/512Mi |
| Flink TaskManager | Flink 1.20+ (PyFlink) | streamflow-processing | 200m/500m | 512Mi/768Mi |
| CloudNativePG Operator | CNPG 1.25+ | streamflow-data | 50m/100m | 64Mi/128Mi |
| PostgreSQL | PostgreSQL 16 | streamflow-data | 200m/500m | 256Mi/512Mi |
| Airflow Webserver | Airflow 2.10+ | streamflow-orchestration | 100m/200m | 256Mi/384Mi |
| Airflow Scheduler | Airflow 2.10+ | streamflow-orchestration | 100m/200m | 256Mi/384Mi |
| Prometheus | Prometheus 2.x | streamflow-monitoring | 100m/200m | 256Mi/384Mi |
| Grafana | Grafana 11.x | streamflow-monitoring | 50m/100m | 128Mi/192Mi |

---

## Architecture Decision Records (ADRs)

### ADR-001: Strimzi KRaft Mode (No ZooKeeper)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Kafka requires metadata management. Traditionally ZooKeeper, now KRaft (built-in).

**Decision:** Use Strimzi with KRaft mode, eliminating ZooKeeper entirely.

**Rationale:**
- KRaft removes the need for a separate ZooKeeper cluster, saving ~512MB RAM
- ZooKeeper is deprecated in Kafka 4.0+
- Strimzi 0.40+ supports KRaft GA
- Single-broker KRaft is simpler to operate

**Alternatives Rejected:**
1. ZooKeeper mode — Wastes 512MB+ RAM on a resource-constrained node
2. External Kafka (Confluent Cloud) — Costs money, defeats $0 budget

---

### ADR-002: LocalExecutor for Airflow (Not KubernetesExecutor)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** KubernetesExecutor spawns one Pod per task. Server has only 9.7GB RAM with 4GB budget for StreamFlow.

**Decision:** Use LocalExecutor. Tasks run in the scheduler process.

**Rationale:**
- KubernetesExecutor spawns ~256MB per task pod. With 4 DAGs running hourly, this could spike to 1GB+ of transient pods
- LocalExecutor uses zero additional pods
- Acceptable for portfolio project (no task isolation needed)

**Alternatives Rejected:**
1. KubernetesExecutor — Too resource-hungry for single-node K3s
2. CeleryExecutor — Requires Redis/RabbitMQ (more pods, more RAM)

---

### ADR-003: Single PostgreSQL Instance (No Replica)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** CloudNativePG supports primary + N replicas.

**Decision:** Single instance (instances: 1). No read replica.

**Rationale:**
- Each PG replica consumes ~256-512MB RAM
- For a portfolio project, HA is not critical — data can be regenerated
- CloudNativePG still manages automated backups to local storage

**Alternatives Rejected:**
1. Primary + 1 replica — 256-512MB extra RAM for HA we don't need
2. External managed PostgreSQL — Costs money

---

### ADR-004: Schemas Over Databases for Medallion Layers

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Medallion layers could be separate databases or schemas within one database.

**Decision:** Single database `streamflow` with 3 schemas: `bronze`, `silver`, `gold`.

**Rationale:**
- Cross-database queries in PostgreSQL require dblink/FDW
- Schemas provide logical separation without cross-DB complexity
- Airflow DAGs can transform data within a single connection
- Standard pattern in Snowflake, BigQuery, Databricks

**Alternatives Rejected:**
1. 3 databases — Cross-DB queries need dblink/FDW
2. Single schema with prefixes — Poor separation, no access control granularity

---

### ADR-005: Terraform + Terragrunt (Not kubectl apply)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** K8s resources can be managed by kubectl, Helm, or Terraform.

**Decision:** Terraform with `kubernetes`, `helm`, and `kubectl` providers, orchestrated by Terragrunt.

**Rationale:**
- State management with plan/apply workflow
- Terragrunt enables DRY configurations across modules
- Pattern used by platform engineering teams at scale
- All infrastructure is code-reviewable

**Alternatives Rejected:**
1. kubectl apply scripts — No state, no rollback, error-prone
2. Helm only — No cross-resource dependencies
3. Pulumi — Less industry adoption for data engineering roles

---

### ADR-006: Python Monorepo Structure

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Flink jobs, Airflow DAGs, generators, and models could be separate packages.

**Decision:** Single `src/` directory with subpackages. Single `pyproject.toml`. Shared models via `src/models/`.

**Rationale:**
- Simpler to navigate, test, and showcase for portfolio
- Shared Pydantic models ensure schema consistency
- Single CI pipeline and single `pytest` run covers everything

**Alternatives Rejected:**
1. Separate repos per component — Overhead without benefit for single developer
2. Separate pyproject.toml per package — Complex dependency management

---

### ADR-007: Terraform Local Backend

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-06 |

**Context:** Terraform state can be stored locally or remotely.

**Decision:** Local backend. State files in `.terraform/` directories (gitignored).

**Rationale:**
- Single developer project, no team collaboration on Terraform
- Remote state requires cloud storage bucket (costs money)
- If state is lost, `terraform import` or recreate from code

**Alternatives Rejected:**
1. S3/GCS remote state — Requires cloud account and costs
2. Kubernetes backend — Experimental, not production-stable

---

### ADR-008: KeyedProcessFunction + RocksDB State

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-07 |

**Context:** Fraud detection requires per-customer state (statistics, location, velocity). Original implementation used Python dicts (lost on restart).

**Decision:** Use Flink `KeyedProcessFunction` with `ValueState<bytes>` backed by RocksDB. Serialization via `to_bytes()`/`from_bytes()` on `CustomerFraudState`.

**Rationale:**
- Fault-tolerant state that survives job restarts
- EXACTLY_ONCE checkpointing guarantees no duplicate alerts
- Savepoint-based upgrades (no state loss during deployments)
- Contract tests ensure serialization compatibility

---

### ADR-009: ML Integration (Offline Training, Online Scoring)

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-07 |

**Context:** Rule-based fraud detection has inherent limitations. ML can capture non-linear patterns.

**Decision:** Isolation Forest model trained offline (`scripts/train_model.py`), loaded in Flink `open()`, scored per-event with alpha blending.

**Rationale:**
- Unsupervised algorithm — no labeled data needed
- 6-feature vector extracted from existing state (no new data sources)
- Alpha blending: `score = alpha * ml + (1-alpha) * rules` allows gradual rollout
- Graceful degradation: if model unavailable, rules-only scoring continues

---

### ADR-010: Dead Letter Queue for Error Handling

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-07 |

**Context:** Malformed events were silently dropped with `logger.warning + return None`.

**Decision:** Route invalid events to `streamflow.dlq` Kafka topic with full error metadata.

**Rationale:**
- Never lose data — every event is either processed or captured in DLQ
- DLQ records include: original event (truncated to 10KB), error type/message, source topic, schema version
- Forward-compatible schema parsing for rolling upgrades

---

### ADR-011: ArgoCD GitOps Deployment

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-07 |

**Context:** Manual `kubectl apply` deployments are error-prone and non-auditable.

**Decision:** ArgoCD Application with auto-sync, self-heal, and prune enabled.

**Rationale:**
- Git is the single source of truth (audit trail for free)
- Auto-sync on push to main branch
- Self-heal corrects manual drift
- Kustomize-based resource management

---

### ADR-012: SLO-Based Monitoring with Error Budgets

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-07 |

**Context:** Alert rules alone don't communicate service reliability targets.

**Decision:** Define 5 SLOs with Prometheus recording rules and error budget alerting.

**Rationale:**
- 99.5% availability target with monthly error budget tracking
- p99 latency < 5s, data freshness < 5 min
- Error budget burn rate alerts before SLO breach
- Google SRE best practices applied to data engineering

---

### ADR-013: dbt Over Raw SQL for Data Transforms

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** Raw SQL files via PostgresOperator had no lineage tracking, no schema testing, and no incremental support.

**Decision:** Replace all raw SQL transforms with dbt-core + dbt-postgres. Models in `staging/`, `intermediate/`, `marts/` with schema tests and custom `generate_schema_name` macro.

**Rationale:**
- Full dependency DAG and lineage tracking
- Schema + singular tests co-located with models
- Incremental processing via `is_incremental()` macro
- Industry-standard analytics engineering tool

Full ADR: [docs/adr/004-dbt-over-raw-sql.md](docs/adr/004-dbt-over-raw-sql.md)

---

### ADR-014: Astronomer Cosmos for dbt + Airflow Integration

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** dbt models need to run inside Airflow. BashOperator is monolithic; custom operators add maintenance burden.

**Decision:** Use Astronomer Cosmos `DbtTaskGroup` with `InvocationMode.SUBPROCESS`. Each dbt model becomes a separate Airflow task with per-model retries and auto-dependency mapping.

**Rationale:**
- Per-model task visibility in Airflow UI
- Automatic `ref()` to Airflow dependency mapping
- Granular retries per model (not per DAG)
- 21M+ monthly downloads, supports Airflow 2.x/3.x

Full ADR: [docs/adr/005-cosmos-airflow-integration.md](docs/adr/005-cosmos-airflow-integration.md)

---

### ADR-015: PyFlink Docker Without Custom JAR

| Attribute | Value |
|-----------|-------|
| **Status** | Accepted |
| **Date** | 2026-02-18 |

**Context:** Flink K8s manifests referenced `streamflow-jobs.jar` which didn't exist. Project uses PyFlink (Python) for all jobs.

**Decision:** Use the built-in `flink-python_2.12-1.20.0.jar` PythonDriver JAR from the base Flink image. Custom Docker image adds Python + PyFlink + scikit-learn.

**Rationale:**
- Zero Java toolchain (no Maven/Gradle)
- Simple Dockerfile: `flink:1.20-java17` base + `pip install`
- Follows official Flink K8s Operator Python examples
- Docker build ~2min vs ~10min for Maven fat JAR

Full ADR: [docs/adr/006-pyflink-docker-no-jar.md](docs/adr/006-pyflink-docker-no-jar.md)

---

## Data Flow

### Streaming Path (Real-time, < 30s latency)

```text
1. DATA GENERATION
   [scripts/generate_events.py]
   ├── Generates realistic Transaction events (Pydantic validated)
   ├── Injects fraud patterns (configurable rate, default 2%)
   └── Produces to Kafka: transactions.raw
        │
2. KAFKA INGESTION
   [transactions.raw — 3 partitions, keyed by customer_id]
   ├── Consumer group: flink-processor → transaction-processor job
   └── Consumer group: flink-fraud → fraud-detector job
        │
3a. TRANSACTION PROCESSING (Flink Job 1)
    [src/flink_jobs/transaction_processor.py]
    ├── Deserialize JSON → validate schema (version-aware)
    ├── Valid → Add processing metadata → JDBC Sink → bronze.raw_transactions
    └── Invalid → DLQ record → Kafka Sink → streamflow.dlq
        │
3b. FRAUD DETECTION (Flink Job 2)
    [src/flink_jobs/fraud_detector_function.py — KeyedProcessFunction]
    ├── Deserialize JSON → extract fields
    ├── Load CustomerFraudState from RocksDB ValueState
    ├── Evaluate 5 rules + ML score (keyed by customer_id):
    │   ├── FR-001: High Value (Welford's algorithm)
    │   ├── FR-002: Velocity (sliding window)
    │   ├── FR-003: Geographic (haversine impossible travel)
    │   ├── FR-004: Time Anomaly (z-score of hour)
    │   ├── FR-005: Blacklist (customer/store lookup)
    │   └── FR-006: ML Anomaly (Isolation Forest, 6-feature vector)
    ├── Compute weighted score: alpha * ml + (1-alpha) * rules
    ├── Persist updated state to RocksDB (EXACTLY_ONCE checkpointing)
    ├── If score >= 0.7 → produce FraudAlert to fraud.alerts
    └── JDBC Sink → bronze.raw_fraud_alerts
```

### Batch Path (Airflow + dbt via Cosmos, hourly)

```text
4. BRONZE → SILVER (DAG: dbt_staging, @hourly)
   [dbt/models/staging/ — Cosmos DbtTaskGroup]
   ├── stg_transactions: incremental from bronze.raw_transactions
   ├── stg_fraud_alerts: incremental from bronze.raw_fraud_alerts
   └── Each dbt model = separate Airflow task (per-model retries)
        │
5. SILVER → GOLD (DAG: dbt_marts, @hourly)
   [dbt/models/intermediate/ + dbt/models/marts/ — Cosmos DbtTaskGroup]
   ├── ExternalTaskSensor waits for dbt_staging completion
   ├── int_customer_stats: customer aggregations
   ├── dim_customer, dim_store: dimension upserts
   ├── fct_transactions, fct_fraud_alerts: fact loads
   └── agg_hourly_sales, agg_daily_fraud: aggregations
        │
6. DATA QUALITY (DAG: dbt_quality, every 15 min)
   [dbt singular tests — Cosmos DbtTaskGroup]
   ├── Schema tests (unique, not_null, accepted_range)
   ├── Singular tests (positive amounts, data freshness)
   └── Per-test visibility in Airflow UI
```

---

## Deployment Sequence

```text
terragrunt run-all apply executes in dependency order:

1. namespaces          ← Creates 5 K8s namespaces
   │
   ├──▶ 2. kafka       ← Strimzi operator + Kafka CRD (KRaft)
   ├──▶ 3. flink       ← Flink K8s Operator Helm
   ├──▶ 4. postgresql   ← CloudNativePG operator + Cluster CRD
   │         │
   │         ├──▶ 5. airflow     ← Airflow Helm (depends on PG for metadata)
   │         │
   └──▶ 6. monitoring   ← kube-prometheus-stack

Post-Terraform:
   7. kubectl apply -f k8s/kafka/kafka-topics.yaml
   8. kubectl apply -f k8s/flink/
   9. kubectl apply -f k8s/monitoring/
  10. python scripts/run_migrations.py --env dev
  11. python scripts/seed_data.py --env dev
```

---

## Security Considerations

| Area | Implementation |
|------|---------------|
| Secrets | PostgreSQL credentials stored as K8s Secret, referenced in Helm values |
| Kafka Auth | PLAINTEXT (internal K8s communication only, no external access) |
| Access | All UIs via `kubectl port-forward` only (no Ingress) |
| Git | `.env.local` and `terraform.tfstate` are gitignored |
| Logs | No PII — transaction amounts logged, customer names/emails are not |
| RBAC | Single namespace admin per streamflow-* namespace |
| Pod Security | runAsNonRoot, runAsUser: 9999, capabilities: drop ALL |
| Network Isolation | 5 NetworkPolicies: default-deny + allow-lists per namespace |
| Disruption Budget | PDBs for Kafka, PostgreSQL, Flink JobManager |
| CI Security | pip-audit dependency scanning, kubeval manifest validation |
| GitOps | ArgoCD auto-sync with self-heal (drift protection) |

---

## Observability

| Aspect | Implementation |
|--------|---------------|
| **Logging** | Structured JSON via Python `logging`. All components log to stdout (K8s collects). |
| **Metrics** | Prometheus scrapes: Kafka (JMX exporter), Flink (prometheus reporter), PG (postgres_exporter), Airflow (StatsD) |
| **Business Metrics** | MetricsCollector: counters, gauges, histograms, timer for business KPIs |
| **Dashboards** | 4 Grafana dashboards provisioned via ConfigMap |
| **Alerting** | AlertManager with 9 rules across Kafka, Flink, PG, and fraud detection |
| **SLOs** | 5 SLO definitions: availability (99.5%), latency (p99<5s), freshness (<5min), error budget, fraud detection (p95<2s) |

---

## Error Handling

| Error Type | Strategy | Retry? | Alert? |
|------------|----------|--------|--------|
| Kafka unavailable | Flink auto-retries with backoff | Yes (built-in) | Yes (restart count > 3) |
| PostgreSQL connection failure | JDBC batch retry with exponential backoff | Yes (3 retries) | Yes (consecutive failures) |
| Malformed JSON event | Log error, skip event, increment metric | No | Yes (error rate > 5%) |
| DAG task failure | Retry 2x with 2min delay | Yes (2 retries) | Yes (DAG SLA miss) |
| OOM on TaskManager | K8s restarts pod, Flink resumes from checkpoint | Yes (automatic) | Yes (restart count) |
| Disk full on PostgreSQL | Maintenance DAG prunes old data | Prevention | Yes (PVC > 80%) |
