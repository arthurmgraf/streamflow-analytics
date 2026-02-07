# StreamFlow Analytics

**Real-time Streaming Data Platform for E-commerce Fraud Detection**

Production-grade streaming pipeline built with Apache Kafka (Strimzi), Apache Flink (PyFlink), Apache Airflow, and PostgreSQL on Kubernetes (K3s). Fully operator-native, infrastructure-as-code, zero-cost deployment.

[![CI](https://github.com/arthurmgraf/streamflow-analytics/actions/workflows/ci.yaml/badge.svg)](https://github.com/arthurmgraf/streamflow-analytics/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://docs.astral.sh/ruff/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

A Brazilian e-commerce company with 200+ physical and online stores needs to:
- **Detect fraud** in credit card transactions within 30 seconds
- **Analyze behavior** patterns across millions of events
- **Generate dashboards** with fresh data (< 1 minute latency)
- **Consolidate data** from POS, website, and mobile sources

StreamFlow Analytics solves this with an end-to-end streaming pipeline: events flow through Kafka, are processed by Flink for real-time fraud detection, persisted in PostgreSQL using Medallion architecture (Bronze/Silver/Gold), orchestrated by Airflow for batch transforms, and monitored via Prometheus + Grafana.

| Metric | Target |
|--------|--------|
| End-to-End Latency | < 30 seconds |
| Throughput | 10,000+ events/second |
| Infrastructure Cost | $0 (on-premise K3s) |
| Test Coverage | > 80% |
| Fraud Detection Rules | 5 rule-based detectors |

---

## Architecture

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│                        K3s CLUSTER (Single-Node)                             │
│                  4 CPU │ 9.7GB RAM │ 598GB Disk                              │
│                  Managed by: Terraform + Terragrunt                          │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─ streamflow-kafka ────────────────────────────────────────────────────┐   │
│  │  Strimzi Operator → Kafka Broker (KRaft, no ZooKeeper)               │   │
│  │  Topics: transactions.raw │ fraud.alerts │ metrics.realtime           │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                              │                                               │
│  ┌─ streamflow-processing ───┼───────────────────────────────────────────┐   │
│  │  Flink K8s Operator → JobManager → TaskManager (2 slots)             │   │
│  │  Jobs: transaction-processor │ fraud-detector │ realtime-aggregator   │   │
│  └───────────────────────────┼───────────────────────────────────────────┘   │
│                              │                                               │
│  ┌─ streamflow-data ─────────┼───────────────────────────────────────────┐   │
│  │  CloudNativePG → PostgreSQL 16                                        │   │
│  │  Schemas: bronze (raw) │ silver (clean) │ gold (star schema)          │   │
│  └───────────────────────────┼───────────────────────────────────────────┘   │
│                              │                                               │
│  ┌─ streamflow-orchestration ┼───────────────────────────────────────────┐   │
│  │  Airflow (LocalExecutor)                                              │   │
│  │  DAGs: bronze_to_silver │ silver_to_gold │ data_quality │ maintenance │   │
│  └───────────────────────────┼───────────────────────────────────────────┘   │
│                              │                                               │
│  ┌─ streamflow-monitoring ───┼───────────────────────────────────────────┐   │
│  │  kube-prometheus-stack → Prometheus + Grafana (4 dashboards)          │   │
│  │  AlertManager: 9 rules across Kafka, Flink, PG, Fraud                │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Key Architecture Decisions (ADRs)

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 001 | Kafka Metadata | KRaft (no ZooKeeper) | Saves ~512MB RAM, ZK deprecated in Kafka 4.0+ |
| 002 | Airflow Executor | LocalExecutor | KubernetesExecutor too resource-hungry for single-node |
| 003 | PostgreSQL HA | Single instance | No replica needed for portfolio project |
| 004 | Medallion Layers | Schemas (not databases) | Single connection, no cross-DB FDW needed |
| 005 | Infrastructure | Terraform + Terragrunt | State management, declarative, code-reviewable |
| 006 | Code Structure | Python monorepo | Shared Pydantic models, single test suite |
| 007 | Terraform State | Local backend | Single developer, $0 cost |

Full ADR documentation: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Fraud Detection Engine

5 rule-based detectors evaluate every transaction in real-time using keyed state per customer:

| Rule | ID | Description | Weight |
|------|----|-------------|--------|
| **High Value** | FR-001 | Transaction > 3x customer average (after 5+ history) | 0.30 |
| **Velocity** | FR-002 | > 5 transactions in 10-minute window | 0.25 |
| **Geographic** | FR-003 | Impossible travel (> 500km in < 1 hour) | 0.20 |
| **Time Anomaly** | FR-004 | Transaction at unusual hour (z-score > 2.0 std dev) | 0.15 |
| **Blacklist** | FR-005 | Customer or store on known fraud list | 0.10 |

**Scoring:** Weighted average of triggered rules. Alert generated when score >= 0.7.

**Algorithms:** Welford's online algorithm for incremental statistics, Haversine formula for geographic distance.

Full documentation: [docs/FRAUD_DETECTION.md](docs/FRAUD_DETECTION.md)

---

## Data Model — Medallion Architecture

```text
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

---

## Technology Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Streaming** | Apache Kafka (Strimzi) | 3.8+ | Event backbone, KRaft mode |
| **Processing** | Apache Flink (PyFlink) | 1.20+ | Stream processing, keyed state |
| **Orchestration** | Apache Airflow | 2.10+ | Batch DAGs, LocalExecutor |
| **Database** | PostgreSQL (CloudNativePG) | 16 | Medallion data warehouse |
| **Infrastructure** | K3s + Terraform + Terragrunt | 1.34 / 1.7+ | Operator-native K8s |
| **Monitoring** | Prometheus + Grafana | - | Metrics, dashboards, alerting |
| **Language** | Python | 3.11+ | Type hints, Pydantic v2, dataclasses |
| **Quality** | ruff + mypy + pytest | - | Linting, type checking, testing |

---

## Repository Structure

```text
streamflow-analytics/
├── src/
│   ├── models/                    # Pydantic v2 data models
│   │   ├── transaction.py         #   Transaction event schema
│   │   ├── customer.py            #   Customer profile schema
│   │   ├── store.py               #   Store reference schema
│   │   └── fraud_alert.py         #   Fraud alert with rule IDs
│   ├── flink_jobs/                # PyFlink streaming jobs
│   │   ├── transaction_processor.py  # Kafka → validate → Bronze
│   │   ├── fraud_detector.py      #   5-rule fraud engine
│   │   └── common/                #   Shared: serialization, state, schemas
│   ├── dags/                      # Airflow DAGs
│   │   ├── bronze_to_silver.py    #   Hourly Bronze → Silver
│   │   ├── silver_to_gold.py      #   Hourly Silver → Gold
│   │   ├── data_quality.py        #   15-min quality checks
│   │   └── maintenance.py         #   Daily prune + vacuum
│   ├── generators/                # Synthetic data generation
│   │   ├── transaction_generator.py  # Realistic Brazilian transactions
│   │   ├── customer_generator.py  #   Customer profiles with risk levels
│   │   ├── store_generator.py     #   10 Brazilian cities
│   │   ├── fraud_patterns.py      #   Fraud injection (4 patterns)
│   │   └── kafka_producer.py      #   Confluent Kafka wrapper
│   └── utils/                     # Shared utilities
│       ├── config.py              #   YAML config loader with merge
│       ├── logging.py             #   Structured JSON logging
│       └── db.py                  #   PostgreSQL connection helper
│
├── sql/
│   ├── migrations/                # DDL: Bronze, Silver, Gold schemas
│   ├── transforms/                # DML: bronze_to_silver, silver_to_gold
│   └── quality/                   # Data quality check queries
│
├── infra/
│   ├── modules/                   # Terraform modules (6)
│   │   ├── namespaces/            #   K8s namespace creation
│   │   ├── strimzi-kafka/         #   Strimzi + Kafka CRD
│   │   ├── flink-operator/        #   Flink K8s Operator
│   │   ├── cloudnativepg/         #   CNPG + PostgreSQL CRD
│   │   ├── airflow/               #   Airflow Helm release
│   │   └── monitoring/            #   kube-prometheus-stack
│   └── environments/
│       └── dev/                   # Terragrunt DRY configs
│
├── k8s/
│   ├── kafka/                     # KafkaTopic CRDs (3 topics)
│   ├── flink/                     # FlinkDeployment CRDs (3 jobs)
│   └── monitoring/                # PrometheusRules, ServiceMonitors, Grafana dashboards
│
├── scripts/
│   ├── generate_events.py         # CLI event generator with rate limiting
│   ├── seed_data.py               # Seed reference data to Silver
│   ├── run_migrations.py          # SQL migration runner
│   ├── verify_pipeline.py         # E2E pipeline health check
│   └── setup.sh                   # Cluster bootstrap script
│
├── tests/
│   ├── unit/                      # 78+ unit tests
│   ├── e2e/                       # End-to-end pipeline tests
│   └── conftest.py                # Shared fixtures
│
├── config/                        # YAML configurations
├── docs/                          # Documentation
├── .github/workflows/             # CI/CD (lint, test, deploy)
├── pyproject.toml                 # Project config (ruff, mypy, pytest)
└── Makefile                       # Dev commands
```

---

## Getting Started

### Prerequisites

- K3s cluster (or any Kubernetes 1.28+)
- Python 3.11+
- Terraform 1.7+ and Terragrunt
- Helm 3.x
- kubectl configured for your cluster

### Quick Setup

```bash
# 1. Clone the repository
git clone https://github.com/arthurmgraf/streamflow-analytics.git
cd streamflow-analytics

# 2. Install Python dependencies
pip install -e ".[dev]"

# 3. Deploy infrastructure (creates 5 namespaces + all operators)
cd infra/environments/dev
terragrunt run-all apply --terragrunt-non-interactive -auto-approve
cd ../../..

# 4. Apply K8s manifests (topics, Flink jobs, monitoring)
kubectl apply -f k8s/kafka/kafka-topics.yaml
kubectl apply -f k8s/flink/
kubectl apply -f k8s/monitoring/

# 5. Run database migrations
python scripts/run_migrations.py --env dev

# 6. Seed reference data
python scripts/seed_data.py --env dev

# 7. Start generating events
python scripts/generate_events.py --rate 100 --duration 600

# 8. Verify pipeline health
python scripts/verify_pipeline.py
```

### Access UIs

```bash
# Grafana (dashboards + monitoring)
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-grafana 3000:80

# Airflow (DAG management)
kubectl port-forward -n streamflow-orchestration svc/airflow-webserver 8080:8080

# Flink (job dashboard)
kubectl port-forward -n streamflow-processing svc/flink-jobmanager 8081:8081
```

---

## Testing

```bash
# Run all unit tests
make test

# Run with coverage report
make test-cov

# Lint + type check
make lint
make typecheck

# Run everything (lint + typecheck + test)
make all

# E2E tests (requires running K3s cluster)
pytest tests/e2e/ -v -m e2e
```

**Quality Results:**
- **ruff:** Zero warnings (strict configuration)
- **mypy:** Zero errors (strict mode, 23+ source files)
- **pytest:** 78+ tests passing

---

## Monitoring

### Grafana Dashboards

| Dashboard | Metrics |
|-----------|---------|
| **Pipeline Overview** | Total events, throughput, latency, error rate |
| **Kafka Metrics** | Consumer lag, messages in/out, partition health |
| **Flink Processing** | Records/sec, checkpoint status, backpressure |
| **Fraud Monitoring** | Alert count, fraud rate, rule breakdown |

### Configured Alerts (9 rules)

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

---

## Batch Pipeline (Airflow DAGs)

| DAG | Schedule | Description |
|-----|----------|-------------|
| `bronze_to_silver` | `@hourly` | Incremental Bronze → Silver transform with dedup |
| `silver_to_gold` | `@hourly` | Build star schema dimensions + facts |
| `data_quality` | `*/15 * * * *` | Null rate, duplicates, freshness, amount checks |
| `maintenance` | `Daily 03:00` | Prune old bronze data + VACUUM ANALYZE |

---

## Documentation

| Document | Description |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | ADRs, component details, data flow |
| [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | Step-by-step setup guide |
| [docs/FRAUD_DETECTION.md](docs/FRAUD_DETECTION.md) | Fraud rules algorithms and tuning |
| [docs/RUNBOOK.md](docs/RUNBOOK.md) | Operations runbook and alert response |

---

## Author

**Arthur Maia Graf**

Senior Data Engineer | Kafka | Flink | Airflow | PostgreSQL | Kubernetes

---

## License

MIT License - see [LICENSE](LICENSE) for details.
