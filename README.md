# StreamFlow Analytics

**Real-time Streaming Fraud Detection Platform for E-commerce**

Production-grade event-driven architecture built with Apache Kafka, Apache Flink, Apache Airflow, and PostgreSQL on Kubernetes. Features ML-augmented fraud detection, Dead Letter Queue, SLO-based monitoring, ArgoCD GitOps, and full observability stack.

[![CI](https://github.com/arthurmaiagraf/streamflow-analytics/actions/workflows/ci.yaml/badge.svg)](https://github.com/arthurmaiagraf/streamflow-analytics/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Coverage >80%](https://img.shields.io/badge/coverage-%3E80%25-brightgreen.svg)]()
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![mypy strict](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Why This Project Exists

A Brazilian e-commerce company with 200+ stores (physical + online) needs to:

- **Detect fraud** in credit card transactions within 30 seconds
- **Score anomalies** using ML (Isolation Forest) combined with rule-based detection
- **Handle failures gracefully** with Dead Letter Queue and schema evolution
- **Serve dashboards** with fresh data (< 1 minute latency)
- **Run on $0 budget** using on-premise K3s

StreamFlow solves this with an event-driven streaming pipeline: transactions flow through Kafka, are processed by Flink with fault-tolerant keyed state (KeyedProcessFunction + RocksDB), scored by ML + 5 business rules, persisted in PostgreSQL using Medallion architecture, orchestrated by Airflow, deployed via ArgoCD GitOps, and monitored with SLO-based Prometheus alerting.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| End-to-End Latency | < 30 seconds |
| Throughput | 10,000+ events/second |
| Infrastructure Cost | $0 (on-premise K3s) |
| Test Coverage | > 80% (208 tests) |
| Fraud Detection | 5 rules + ML (Isolation Forest) |
| Deployment | ArgoCD GitOps with auto-sync |
| Checkpointing | EXACTLY_ONCE with RocksDB |
| SLO Target | 99.5% availability |

---

## Architecture

```
                                    ┌──────────────────────────────────────┐
                                    │        K3s CLUSTER (Single-Node)     │
                                    │    4 CPU | 9.7GB RAM | 598GB Disk   │
                                    │    Managed by: Terraform + Terragrunt│
┌─────────────────┐                 ├──────────────────────────────────────┤
│  Event Sources   │                │                                      │
│ ─────────────── │  Kafka Producer │  streamflow-kafka (Strimzi/KRaft)   │
│ POS Terminals   │ ──────────────▶ │  ┌──────────────────────────────┐   │
│ Website         │                 │  │ transactions.raw (3 partitions)│   │
│ Mobile App      │                 │  │ fraud.alerts                  │   │
│ Synthetic Gen   │                 │  │ metrics.realtime              │   │
│                 │                 │  │ streamflow.dlq (Dead Letter)  │   │
└─────────────────┘                 │  └──────────────┬───────────────┘   │
                                    │                 │                    │
                                    │  streamflow-processing (Flink K8s)  │
                                    │  ┌──────────────▼───────────────┐   │
                                    │  │ transaction-processor        │   │
                                    │  │   └─▶ Parse + Validate      │   │
                                    │  │   └─▶ DLQ (malformed events)│   │
                                    │  │                              │   │
                                    │  │ fraud-detector (KeyedProcess)│   │
                                    │  │   └─▶ 5 Rules + ML Score   │   │
                                    │  │   └─▶ RocksDB State        │   │
                                    │  │   └─▶ EXACTLY_ONCE         │   │
                                    │  │                              │   │
                                    │  │ realtime-aggregator          │   │
                                    │  │   └─▶ Windowed Metrics     │   │
                                    │  └──────────────┬───────────────┘   │
                                    │                 │                    │
                                    │  streamflow-data (CloudNativePG)    │
                                    │  ┌──────────────▼───────────────┐   │
                                    │  │ PostgreSQL 16                │   │
                                    │  │  bronze.* (raw events)      │   │
                                    │  │  silver.* (cleaned, deduped)│   │
                                    │  │  gold.*   (star schema)     │   │
                                    │  └──────────────┬───────────────┘   │
                                    │                 │                    │
                                    │  streamflow-orchestration (Airflow) │
                                    │  ┌──────────────▼───────────────┐   │
                                    │  │ bronze_to_silver  (@hourly)  │   │
                                    │  │ silver_to_gold    (@hourly)  │   │
                                    │  │ data_quality      (*/15 min) │   │
                                    │  │ maintenance       (@daily)   │   │
                                    │  └─────────────────────────────┘   │
                                    │                                      │
                                    │  streamflow-monitoring               │
                                    │  ┌─────────────────────────────┐    │
                                    │  │ Prometheus + Grafana         │    │
                                    │  │ 4 Dashboards | 9 Alert Rules│    │
                                    │  │ 5 SLO Definitions           │    │
                                    │  │ Error Budget Tracking        │    │
                                    │  └─────────────────────────────┘    │
                                    └──────────────────────────────────────┘
```

---

## Fraud Detection Engine

### Hybrid Approach: Rules + ML

The fraud detector uses a `KeyedProcessFunction` with fault-tolerant state backed by RocksDB. Each customer's state (transaction history, statistics, location) is checkpointed with EXACTLY_ONCE semantics.

**5 Business Rules:**

| Rule | ID | Logic | Weight |
|------|----|-------|--------|
| High Value | FR-001 | Amount > 3x customer average (after 5+ txns) | 0.30 |
| Velocity | FR-002 | > 5 transactions in 10-minute window | 0.25 |
| Geographic | FR-003 | Impossible travel (> 500km in < 1 hour, Haversine) | 0.20 |
| Time Anomaly | FR-004 | Unusual hour (z-score > 2.0 via Welford's algorithm) | 0.15 |
| Blacklist | FR-005 | Customer or store on fraud list | 0.10 |

**ML Scoring (FR-006):**

| Component | Detail |
|-----------|--------|
| Algorithm | Isolation Forest (unsupervised anomaly detection) |
| Features | 6-dimensional vector: amount_zscore, velocity_count, time_deviation, geo_speed_kmh, is_blacklisted, amount_ratio |
| Training | Offline on synthetic data (10k transactions) |
| Integration | `score_final = alpha * ml_score + (1 - alpha) * rules_score` (alpha=0.3) |
| Score Range | Normalized to [0, 1] via decision_function mapping |

**Final Score:** Weighted combination of rules + ML. Alert generated when `score >= 0.7`.

### State Management

```
CustomerFraudState (per customer_id, in RocksDB ValueState)
├── amount_stats: RunningStats  (Welford's online algorithm, O(1) memory)
├── hour_stats: RunningStats    (transaction hour distribution)
├── last_location: GeoLocation  (lat, lon, timestamp)
├── velocity_window: list[float] (10-min sliding window timestamps)
├── is_blacklisted: bool
└── Serialization: JSON via to_bytes()/from_bytes()
    └── Contract tests ensure checkpoint compatibility
```

---

## Dead Letter Queue

Malformed events are routed to a Dead Letter Queue instead of being silently dropped:

```
transactions.raw ──▶ transaction-processor
                         │
                         ├── Valid ──▶ Bronze tables
                         │
                         └── Invalid ──▶ streamflow.dlq topic
                                          │
                                          ├── original_event (truncated to 10KB)
                                          ├── error_type + error_message
                                          ├── source_topic + timestamp
                                          └── schema_version (forward-compatible)
```

Schema evolution uses version-aware parsing: unknown schema versions trigger a warning but attempt best-effort parsing, ensuring forward compatibility during rolling upgrades.

---

## Data Model: Medallion Architecture

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│   BRONZE LAYER   │      │   SILVER LAYER   │      │    GOLD LAYER    │
│   (Raw Events)   │      │   (Cleaned)      │      │  (Star Schema)   │
│ ──────────────── │      │ ──────────────── │      │ ──────────────── │
│ raw_transactions │ ───▶ │ clean_transactions│ ───▶ │ fact_transactions│
│ raw_fraud_alerts │      │ customers        │      │ fact_fraud_alerts│
│                  │      │ stores           │      │ dim_customer     │
│                  │      │ products         │      │ dim_store        │
│                  │      │                  │      │ dim_product      │
│                  │      │                  │      │ dim_date         │
│                  │      │                  │      │ agg_hourly_sales │
│                  │      │                  │      │ agg_daily_fraud  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
   Flink JDBC Sink           Airflow @hourly           Airflow @hourly
   (real-time)               (incremental)             (star schema)
```

All layers coexist as PostgreSQL schemas (not separate databases) — single connection, no cross-DB foreign data wrappers needed.

---

## Technology Stack

| Category | Technology | Purpose |
|----------|-----------|---------|
| **Streaming** | Apache Kafka (Strimzi, KRaft) | Event backbone, no ZooKeeper |
| **Processing** | Apache Flink (PyFlink, K8s Operator) | KeyedProcessFunction, RocksDB state, EXACTLY_ONCE |
| **ML** | scikit-learn (Isolation Forest) | Unsupervised anomaly detection |
| **Orchestration** | Apache Airflow (LocalExecutor) | Batch DAGs with TaskGroups, SLA, callbacks |
| **Database** | PostgreSQL 16 (CloudNativePG) | Medallion architecture (Bronze/Silver/Gold) |
| **Infrastructure** | K3s + Terraform + Terragrunt | Operator-native Kubernetes, IaC |
| **Deployment** | ArgoCD | GitOps with auto-sync, self-heal, prune |
| **Monitoring** | Prometheus + Grafana | 4 dashboards, 9 alert rules, 5 SLOs |
| **Security** | NetworkPolicies + PDBs | Namespace isolation, non-root pods |
| **CI/CD** | GitHub Actions | Lint, typecheck, test matrix, security audit, K8s validation |
| **Quality** | ruff + mypy --strict + pytest | Zero warnings, zero type errors, 208+ tests |

---

## Architecture Decisions (ADRs)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 001 | Kafka Metadata | KRaft (no ZooKeeper) | Saves ~512MB RAM, ZK deprecated in Kafka 4.0+ |
| 002 | Airflow Executor | LocalExecutor | KubernetesExecutor too resource-hungry for single-node |
| 003 | PostgreSQL HA | Single instance | No replica needed for portfolio project |
| 004 | Medallion Layers | Schemas (not databases) | Single connection, no cross-DB FDW needed |
| 005 | Infrastructure | Terraform + Terragrunt | State management, declarative, code-reviewable |
| 006 | Code Structure | Python monorepo | Shared Pydantic models, single test suite |
| 007 | Terraform State | Local backend | Single developer, $0 cost |
| 008 | Fraud State | KeyedProcessFunction + RocksDB | Fault-tolerant, survives restarts, EXACTLY_ONCE |
| 009 | ML Integration | Offline training, online scoring | Isolation Forest loaded in Flink open(), scored per-event |
| 010 | Error Handling | Dead Letter Queue | Never lose data, investigate failures later |
| 011 | Deployment | ArgoCD GitOps | Auto-sync, self-heal, declarative, audit trail |
| 012 | Monitoring | SLO-based with error budgets | 99.5% availability, p99 latency < 5s |

Full ADR documentation: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Repository Structure

```
streamflow-analytics/
├── src/
│   ├── models/                          # Pydantic v2 data models
│   │   ├── transaction.py               #   Transaction event schema
│   │   ├── customer.py                  #   Customer profile
│   │   ├── store.py                     #   Store reference
│   │   └── fraud_alert.py               #   Alert with FR-001..FR-006
│   ├── flink_jobs/                      # PyFlink streaming jobs
│   │   ├── transaction_processor.py     #   Kafka -> validate -> Bronze (DLQ for invalid)
│   │   ├── fraud_detector.py            #   FraudRuleEvaluator (5 rules, pure Python)
│   │   ├── fraud_detector_function.py   #   KeyedProcessFunction (Flink state)
│   │   ├── fraud_pipeline.py            #   Pipeline builder (source -> keyed -> sinks)
│   │   ├── common/
│   │   │   ├── state.py                 #   CustomerFraudState, RunningStats, GeoLocation
│   │   │   ├── serialization.py         #   Schema-versioned JSON serialization
│   │   │   ├── dlq.py                   #   Dead Letter Queue record builder
│   │   │   └── schemas.py              #   Flink SQL schema definitions
│   │   └── ml/
│   │       ├── feature_engineering.py   #   6-feature vector extraction
│   │       └── model_scorer.py          #   Isolation Forest scorer [0,1]
│   ├── dags/                            # Airflow DAGs
│   │   ├── bronze_to_silver.py          #   TaskGroups, SLA, callbacks
│   │   ├── silver_to_gold.py            #   Per-dimension/fact tasks
│   │   ├── data_quality.py              #   4 quality checks (null, dup, fresh, amount)
│   │   ├── maintenance.py               #   Prune + VACUUM with notifications
│   │   └── common/callbacks.py          #   Shared failure/success/SLA callbacks
│   ├── generators/                      # Synthetic data generation
│   │   ├── transaction_generator.py     #   Realistic Brazilian transactions
│   │   ├── customer_generator.py        #   Customer profiles with risk levels
│   │   ├── store_generator.py           #   10 Brazilian cities
│   │   ├── fraud_patterns.py            #   Fraud injection (4 patterns)
│   │   └── kafka_producer.py            #   Confluent Kafka wrapper
│   └── utils/
│       ├── config.py                    #   YAML config loader with merge
│       ├── logging.py                   #   Structured JSON logging
│       ├── db.py                        #   PostgreSQL connection helper
│       └── metrics.py                   #   Business metrics collector
│
├── tests/
│   ├── unit/                            # 13 test files, 160+ tests
│   │   ├── test_models.py               #   Pydantic model validation
│   │   ├── test_fraud_detector.py       #   FraudRuleEvaluator rules
│   │   ├── test_fraud_rule_evaluator.py #   Renamed evaluator tests
│   │   ├── test_fraud_detector_function.py  # KeyedProcessFunction mocks
│   │   ├── test_feature_engineering.py  #   Feature vector extraction
│   │   ├── test_model_scorer.py         #   ML scorer range [0,1]
│   │   ├── test_dlq.py                  #   DLQ record structure
│   │   ├── test_serialization.py        #   Schema-versioned parsing
│   │   ├── test_state_serialization.py  #   to_bytes()/from_bytes()
│   │   ├── test_generators.py           #   Transaction/fraud generation
│   │   ├── test_config.py               #   Config loading + merge
│   │   └── test_metrics.py              #   MetricsCollector
│   ├── integration/                     # Cross-module integration
│   │   ├── test_full_pipeline.py        #   Generator -> Fraud Engine flow
│   │   └── test_ml_pipeline.py          #   State -> Features -> ML Score
│   ├── contract/                        # Schema compatibility contracts
│   │   ├── test_transaction_schema.py   #   Transaction producer/consumer
│   │   ├── test_fraud_alert_schema.py   #   Alert schema guarantee
│   │   ├── test_dlq_schema.py           #   DLQ record structure
│   │   └── test_state_compat.py         #   State serialization roundtrip
│   └── conftest.py                      #   Shared fixtures (state, ML, transactions)
│
├── sql/
│   ├── migrations/                      #   001-004: Bronze, Silver, Gold, Indexes
│   ├── transforms/
│   │   ├── bronze_to_silver.sql         #   Incremental dedup transform
│   │   ├── silver_to_gold.sql           #   Star schema build
│   │   ├── update_customer_stats.sql
│   │   └── gold/                        #   Per-dimension/fact SQL (7 files)
│   └── quality/                         #   Per-check SQL (4 files)
│
├── infra/
│   ├── modules/                         #   6 Terraform modules
│   │   ├── namespaces/                  #   K8s namespace creation
│   │   ├── strimzi-kafka/               #   Strimzi + Kafka CRD
│   │   ├── flink-operator/              #   Flink K8s Operator
│   │   ├── cloudnativepg/               #   CNPG + PostgreSQL CRD
│   │   ├── airflow/                     #   Airflow Helm release
│   │   └── monitoring/                  #   kube-prometheus-stack
│   └── environments/dev/                #   Terragrunt DRY configs
│
├── k8s/
│   ├── kafka/kafka-topics.yaml          #   4 KafkaTopics (incl. DLQ)
│   ├── flink/                           #   3 FlinkDeployments
│   │   ├── fraud-detector.yaml          #     RocksDB, EXACTLY_ONCE, savepoint
│   │   ├── transaction-processor.yaml   #     Security context, Prometheus
│   │   └── realtime-aggregator.yaml     #     Non-root, capabilities dropped
│   ├── security/
│   │   ├── network-policies.yaml        #   5 NetworkPolicies (namespace isolation)
│   │   └── pod-disruption-budgets.yaml  #   3 PDBs (Kafka, PG, Flink)
│   ├── monitoring/
│   │   ├── service-monitors.yaml        #   Prometheus ServiceMonitors
│   │   ├── alerting-rules.yaml          #   9 PrometheusRules
│   │   └── slo-rules.yaml              #   5 SLO definitions + error budgets
│   ├── argocd/application.yaml          #   GitOps Application (auto-sync, self-heal)
│   └── kustomization.yaml              #   Kustomize base for all resources
│
├── scripts/
│   ├── deploy.sh                        #   Deploy (ArgoCD/kubectl) + smoke tests
│   ├── setup.sh                         #   Cluster bootstrap
│   ├── generate_events.py               #   CLI event generator
│   ├── seed_data.py                     #   Seed Silver reference data
│   ├── run_migrations.py                #   SQL migration runner
│   ├── verify_pipeline.py               #   E2E health check
│   └── train_model.py                   #   Offline ML model training
│
├── config/                              #   YAML configurations
├── docs/                                #   ARCHITECTURE, FRAUD_DETECTION, RUNBOOK
├── .github/workflows/
│   ├── ci.yaml                          #   Lint + Type + Test matrix + Security + K8s
│   └── deploy.yaml                      #   ArgoCD/kubectl deploy + smoke tests
├── pyproject.toml                       #   ruff, mypy, pytest config
└── Makefile                             #   Dev commands (18 targets)
```

---

## Getting Started

### Prerequisites

- K3s cluster (or any Kubernetes 1.28+)
- Python 3.11+
- Terraform 1.7+ and Terragrunt
- kubectl configured for your cluster

### Quick Setup

```bash
# 1. Clone and install
git clone https://github.com/arthurmaiagraf/streamflow-analytics.git
cd streamflow-analytics
pip install -e ".[dev]"

# 2. Deploy infrastructure (5 namespaces + all operators)
bash scripts/setup.sh

# 3. Deploy application (security + Kafka + Flink + monitoring)
make deploy

# 4. Run database migrations
python scripts/run_migrations.py --env dev

# 5. Seed reference data
python scripts/seed_data.py --env dev

# 6. Train ML model (optional — generates models/fraud_model.joblib)
python scripts/train_model.py

# 7. Start generating events
python scripts/generate_events.py --rate 100 --duration 600

# 8. Verify everything
python scripts/verify_pipeline.py
```

### Alternative: ArgoCD GitOps Deploy

```bash
# One command — ArgoCD handles everything via Git sync
make deploy-argocd

# ArgoCD will auto-sync on every git push to main
# Self-heal if someone manually changes resources
# Prune resources removed from Git
```

### Access UIs

```bash
# Grafana (4 dashboards + SLO tracking)
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-grafana 3000:80

# Airflow (5 DAGs with TaskGroups)
kubectl port-forward -n streamflow-orchestration svc/airflow-webserver 8080:8080

# Flink (job dashboard + checkpoints)
kubectl port-forward -n streamflow-processing svc/flink-jobmanager 8081:8081

# ArgoCD (GitOps dashboard)
kubectl port-forward svc/argocd-server -n argocd 8443:443
```

---

## Testing

```bash
# Full test suite (208 tests)
make test

# By category
make test-unit          # Unit tests (160+ tests)
make test-contract      # Schema contract tests (48 tests)
make test-integration   # Cross-module integration (10 tests)

# With coverage
make test-cov           # Fails if < 80% coverage

# Quality gates
make lint               # ruff (strict: E, F, I, UP, B, SIM, N, RUF)
make typecheck          # mypy --strict (zero errors)
make check              # lint + typecheck + test (all in one)
```

### Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| **Unit** | 160+ | Individual function/class behavior |
| **Contract** | 48 | Schema compatibility between producers/consumers |
| **Integration** | 10 | Cross-module flows (Generator -> Engine -> Alert) |

**Contract tests** guarantee that schema changes don't break downstream consumers. They validate:
- Required fields and validation rules
- Serialization format compatibility
- State checkpoint roundtrip safety (to_bytes/from_bytes)
- Forward compatibility for schema evolution

---

## Monitoring & Observability

### Grafana Dashboards

| Dashboard | Key Metrics |
|-----------|-------------|
| **Pipeline Overview** | Total events, throughput, latency, error rate |
| **Kafka Metrics** | Consumer lag, messages in/out, partition health |
| **Flink Processing** | Records/sec, checkpoint duration, backpressure |
| **Fraud Monitoring** | Alert count, fraud rate, rule breakdown, ML scores |

### Alert Rules (9)

| Alert | Condition | Severity |
|-------|-----------|----------|
| KafkaConsumerLagHigh | Lag > 10,000 events | Warning |
| KafkaBrokerDown | Broker offline > 2 min | Critical |
| FlinkJobNotRunning | Job state != RUNNING > 5 min | Critical |
| FlinkCheckpointFailing | No checkpoint > 10 min | Warning |
| PostgresHighConnections | > 80% connections used | Warning |
| PostgresPVCNearlyFull | Disk > 80% | Critical |
| HighFraudRate | > 5% fraud in 1 hour | Warning |
| PipelineLatencyHigh | E2E latency > 60s | Warning |
| AirflowDAGFailure | DAG failure | Warning |

### SLO Definitions (5)

| SLO | Target | Window |
|-----|--------|--------|
| Availability | 99.5% | 30 days |
| Latency (p99) | < 5 seconds | 5 min |
| Data Freshness | < 5 minutes | 10 min |
| Error Budget | Monthly burn rate | 30 days |
| Fraud Detection (p95) | < 2 seconds | 5 min |

---

## Batch Pipeline (Airflow DAGs)

| DAG | Schedule | Tasks | Features |
|-----|----------|-------|----------|
| `bronze_to_silver` | `@hourly` | 6 | TaskGroups, pre/post validation, SLA |
| `silver_to_gold` | `@hourly` | 9 | Per-dimension/fact tasks, parallel dims |
| `data_quality` | `*/15 min` | 5 | 4 SQL checks + alert notification |
| `maintenance` | `Daily 03:00` | 4 | Parallel prune + VACUUM ANALYZE |

All DAGs include: structured callbacks (failure/success/SLA miss), exponential retry, pool-based concurrency.

---

## Kubernetes Security

| Control | Implementation |
|---------|---------------|
| **Pod Security** | runAsNonRoot, runAsUser: 9999, capabilities: drop ALL |
| **Network Isolation** | 5 NetworkPolicies (default-deny + allow-lists) |
| **Disruption Budget** | PDBs for Kafka, PostgreSQL, Flink JobManager |
| **GitOps** | ArgoCD auto-sync with self-heal (drift protection) |
| **CI Security** | pip-audit dependency scanning, kubeval manifest validation |

---

## CI/CD Pipeline

```
Push to main/PR
    │
    ├── Lint (ruff check)
    ├── Type Check (mypy --strict)
    ├── Security (pip-audit)
    └── K8s Validate (kubeval)
            │
            ▼
    Test Matrix (Python 3.11 + 3.12)
        ├── Unit Tests
        ├── Contract Tests
        ├── Integration Tests
        └── Coverage Report (>80%)
            │
            ▼ (manual trigger)
    Deploy
        ├── Pre-deploy (contract tests + kubeval)
        ├── Deploy (ArgoCD sync OR kubectl apply)
        └── Post-deploy Smoke Tests
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | ADRs, component details, data flow |
| [ROADMAP.md](ROADMAP.md) | Staff-level upgrade plan and phases |
| [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Step-by-step setup guide |
| [docs/FRAUD_DETECTION.md](docs/FRAUD_DETECTION.md) | Fraud rules, ML integration, tuning |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Operations runbook and alert response |

---

## Author

**Arthur Maia Graf**

Staff Data Engineer | Kafka | Flink | Airflow | PostgreSQL | Kubernetes | ML

---

## License

MIT License - see [LICENSE](LICENSE) for details.
