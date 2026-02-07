# BRAINSTORM: StreamFlow Analytics

> Exploratory session to clarify intent and approach for a production-grade streaming data platform

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | STREAMFLOW_ANALYTICS |
| **Date** | 2026-02-06 |
| **Author** | brainstorm-agent |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** Projeto end-to-end de portfólio para Senior/Staff Data Engineer. Plataforma de streaming em tempo real para detecção de fraude em e-commerce, usando Apache Kafka, Flink (PyFlink), Airflow, PostgreSQL, deploy em K3s on-premise com Terraform/Terragrunt.

**Context Gathered:**
- Repositório existe com README.md detalhado mas NENHUM código implementado
- Estrutura `.claude/` ecosystem está configurada (agents, skills, KB)
- Usuário tem servidor K3s on-premise acessível via SSH
- Foco em qualidade de código production-ready, não apenas features
- Budget: $0 (tudo open-source, infraestrutura própria)

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `src/`, `infra/`, `scripts/` | Reorganizar estrutura do README para match |
| Relevant KB Domains | terraform, terragrunt (existentes) | Padrões de IaC já disponíveis na KB |
| IaC Patterns | Terraform + Terragrunt (confirmado) | Usar módulos reutilizáveis por operador |
| Deployment | K3s on-premise (sem Docker Compose) | Helm charts + CRDs via Terraform |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Qual o objetivo primário do projeto no portfólio? | **Arquitetura + Código Production-Ready** | Foco em qualidade, testes, IaC, documentação. Menos features, tudo com padrão de produção. Impressiona tech leads. |
| 2 | Pretende rodar de verdade ou apenas documentar? | **K3s on-premise real + Terraform/Terragrunt** | Eleva projeto de playground para deployment real. Absurdamente mais impressionante. |
| 3 | Estratégia de deployment? | **K3s apenas (sem Docker Compose)** | Foco total em Kubernetes. Mostra que opera em ambientes reais, não playgrounds. |
| 4 | Nível de realismo dos dados? | **Dataset público real + gerador sintético** | Usar dataset de fraude do Kaggle como seed + gerador Python para streaming. Mostra trabalho com dados reais. |
| 5 | Escopo de testes e qualidade? | **Full Quality Stack** | pytest, ruff, mypy, pre-commit hooks, coverage >80%. Diferencial de Staff Engineer. |
| 6 | Material de referência? | **Nenhum - começar do zero** | Construir tudo baseado em best practices da indústria. |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input files | Kaggle (Credit Card Fraud Detection) | ~284k transactions | Dataset Andrea Dal Pozzolo. 492 fraudes (0.17%). Campos: Time, V1-V28 (PCA), Amount, Class |
| Input files | Kaggle (IEEE-CIS Fraud Detection) | ~590k transactions | Mais rico em features. TransactionDT, TransactionAmt, ProductCD, card1-6, addr1-2, emails, device info |
| Output examples | N/A | 0 | A definir na fase Define |
| Ground truth | Incluído nos datasets | Labels | Fraud/Not-Fraud labels para validação |
| Related code | N/A | 0 | Projeto greenfield |

**How samples will be used:**

- **Seed data:** Dataset real como base para distribuições estatísticas (valores, horários, padrões)
- **Generator calibration:** Calibrar gerador sintético para produzir dados com distribuições realistas
- **Test fixtures:** Subsets do dataset para testes unitários e integração
- **Fraud patterns:** Extrair padrões reais de fraude para as regras de detecção

---

## Approaches Explored

### Approach A: Operator-Native Architecture ⭐ Recommended

**Description:** Cada serviço stateful gerenciado por seu Kubernetes operator nativo. Toda infraestrutura provisionada via Terraform/Terragrunt. Código Python production-ready com full test coverage.

**Stack Completo:**

| Componente | Tecnologia | Deployment |
|-----------|-----------|------------|
| Event Streaming | Apache Kafka 3.7+ | Strimzi Operator (CRDs) |
| Stream Processing | Apache Flink 1.18+ (PyFlink) | Flink Kubernetes Operator (CRDs) |
| Batch Orchestration | Apache Airflow 2.8+ | Official Helm Chart + KubernetesExecutor |
| Data Warehouse | PostgreSQL 16+ | CloudNativePG Operator |
| Monitoring | Prometheus + Grafana | kube-prometheus-stack Helm |
| IaC | Terraform + Terragrunt | Modules por operator/namespace |
| Language | Python 3.11+ | PyFlink, DAGs, scripts, generators |
| Quality | ruff + mypy + pytest + pre-commit | Full CI pipeline |

**Pros:**
- Mais profissional e production-like possível
- Self-healing para serviços stateful (Kafka, PostgreSQL)
- Demonstra domínio profundo de Kubernetes operators e CRDs
- Cada componente gerenciado declarativamente
- Padrão real de empresas como Netflix, Uber, Spotify

**Cons:**
- Mais complexo de configurar inicialmente
- Requer entendimento de CRDs e operator patterns
- Debugging pode ser mais difícil (mais camadas de abstração)

**Why Recommended:** Para portfólio de Staff Data Engineer, operator-native é o padrão da indústria. Mostra que o candidato entende Kubernetes em profundidade, não apenas "deploy with Helm". Tech leads ficam impressionados com CRDs customizados e operator patterns.

---

### Approach B: Helm-Only Architecture

**Description:** Todos os serviços deployados via Helm charts (Bitnami/community), sem operators customizados.

**Pros:**
- Setup mais rápido (~50% menos YAML)
- Documentação abundante
- Menor curva de aprendizado

**Cons:**
- Menos impressionante para portfólio senior
- Sem self-healing avançado para stateful services
- Não demonstra conhecimento de operators/CRDs
- Padrão mais associado a deployments de dev/staging

---

### Approach C: Managed Services Simulation

**Description:** Arquitetar como se usasse serviços gerenciados (Confluent Cloud, Amazon MSK, Cloud Composer), implementando equivalentes open-source.

**Pros:**
- Mostra entendimento de cloud patterns
- Interfaces similares a serviços managed

**Cons:**
- Abstração desnecessária para on-premise
- Pode parecer over-engineered
- Não mostra domínio real de Kubernetes

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A: Operator-Native Architecture |
| **User Confirmation** | 2026-02-06 |
| **Reasoning** | Máxima profissionalidade. Padrão de Staff Engineer. Self-healing. Demonstra domínio profundo de K8s. |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | K3s-only (sem Docker Compose) | Deploy real impressiona mais que playground local | Docker Compose local + K3s prod |
| 2 | Operator-native para stateful services | Production pattern, self-healing, CRDs | Helm-only (menos impressionante) |
| 3 | Dataset real + gerador sintético | Mostra trabalho com dados reais + capacidade de simular | Dados sintéticos simples (Faker) |
| 4 | Full quality stack (pytest/ruff/mypy) | Diferencial de Staff Engineer | Testes mínimos |
| 5 | Rule-based fraud detection (sem ML) | Foco em Data Engineering, não Data Science | ML model integration |
| 6 | PostgreSQL como DW (Medallion) | Custo zero, ACID, SQL completo | Nenhum - já definido no README |
| 7 | Terraform + Terragrunt | IaC production-grade, DRY | Helm install manual |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| ML Model Integration (sklearn/xgboost) | Escopo de Data Science, não DE. Rule-based é suficiente e mais demonstrável | Yes (Phase 3+) |
| Recomendações personalizadas | Fora do escopo de Data Engineering | Yes |
| Análise de churn | Escopo de DS/ML, não pipeline engineering | Yes |
| Forecasting de vendas | Idem | Yes |
| A/B testing framework | Over-engineering para portfólio | Yes |
| Kafka Connect (Debezium CDC) | Adiciona complexidade sem valor proporcional para MVP | Yes (Phase 2+) |
| 200+ stores simulation | 10 stores é suficiente para demonstrar | Yes |
| Mobile App + POS como fontes separadas | Um gerador unificado é mais pragmático | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Visão geral arquitetura (K3s + Operators) | ✅ | "Pode seguir assim desde que não haja nenhum custo" | No - confirmado $0 |
| 3 Abordagens (Operator vs Helm vs Managed) | ✅ | Selecionou Approach A: Operator-Native | No |
| YAGNI (remover ML/DS features) | ✅ | "Concordo totalmente" | No |

---

## Project Architecture (Detailed)

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     K3s CLUSTER (On-Premise)                        │
│                     Managed by Terraform + Terragrunt               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  namespace: streamflow-kafka                                         │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Strimzi Operator                                              │  │
│  │  ├─ KafkaCluster (3 brokers, KRaft mode)                      │  │
│  │  ├─ KafkaTopic CRDs (transactions, events, fraud-alerts)      │  │
│  │  └─ KafkaUser CRDs (flink-consumer, airflow-consumer)         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  namespace: streamflow-processing                                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Flink Kubernetes Operator                                     │  │
│  │  ├─ FlinkDeployment: transaction-processor (PyFlink)          │  │
│  │  ├─ FlinkDeployment: fraud-detector (PyFlink)                 │  │
│  │  └─ FlinkDeployment: realtime-aggregator (PyFlink)            │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                              │                                       │
│                              ▼                                       │
│  namespace: streamflow-data                                          │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  CloudNativePG Operator                                        │  │
│  │  ├─ PostgreSQL Cluster (primary + 1 replica)                  │  │
│  │  ├─ Databases: bronze_db, silver_db, gold_db                  │  │
│  │  └─ Automated backups + WAL archiving                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  namespace: streamflow-orchestration                                 │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Apache Airflow (Helm)                                         │  │
│  │  ├─ KubernetesExecutor (cada task = 1 Pod)                    │  │
│  │  ├─ DAG: bronze_to_silver (hourly)                            │  │
│  │  ├─ DAG: silver_to_gold (hourly)                              │  │
│  │  ├─ DAG: data_quality_checks (15min)                          │  │
│  │  └─ DAG: maintenance (daily)                                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  namespace: streamflow-monitoring                                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  kube-prometheus-stack (Helm)                                  │  │
│  │  ├─ Prometheus (scraping Kafka, Flink, PG, Airflow metrics)   │  │
│  │  ├─ Grafana (4 dashboards: Pipeline, Kafka, Flink, Fraud)    │  │
│  │  └─ AlertManager (Slack/email alerts)                         │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
[Data Generator]  ──Produce──▶  [Kafka Topics]
  (Python script)                  │
  Seeds: Kaggle dataset            ├─ transactions.raw
  Synthetic: Faker + patterns      ├─ events.raw
                                   └─ fraud-alerts
                                       │
                    ┌──────────────────┘
                    ▼
            [Flink PyFlink Jobs]
            ├─ transaction_processor.py
            │   └─ Validate → Enrich → Write Bronze
            ├─ fraud_detector.py
            │   └─ Apply Rules → Score → Alert if fraud
            └─ realtime_aggregator.py
                └─ Window (1min, 5min, 1h) → Metrics
                    │
                    ▼
            [PostgreSQL (CloudNativePG)]
            ├─ BRONZE: raw_transactions, raw_events
            ├─ SILVER: clean_transactions, enriched_events
            └─ GOLD: fact_transactions, dim_*, agg_*
                    │
                    │ Airflow DAGs (hourly)
                    │ Bronze → Silver → Gold
                    ▼
            [Grafana Dashboards]
            ├─ Pipeline Overview
            ├─ Kafka Metrics
            ├─ Flink Processing
            └─ Fraud Monitoring
```

### Medallion Architecture in PostgreSQL

```
BRONZE (raw, immutable)          SILVER (cleaned, enriched)        GOLD (business-ready)
─────────────────────           ──────────────────────────        ────────────────────────
raw_transactions                 clean_transactions                 fact_transactions
├─ id (PK)                      ├─ transaction_id (PK)            ├─ transaction_key (PK)
├─ kafka_topic                  ├─ customer_id (FK)               ├─ date_key (FK → dim_date)
├─ kafka_partition              ├─ store_id (FK)                  ├─ customer_key (FK)
├─ kafka_offset                 ├─ product_id (FK)                ├─ store_key (FK)
├─ event_timestamp              ├─ amount (validated)             ├─ product_key (FK)
├─ raw_payload (JSONB)          ├─ currency (normalized)          ├─ amount
├─ ingested_at                  ├─ fraud_score                    ├─ fraud_flag
├─ processing_status            ├─ is_valid                       └─ processing_timestamp
└─ schema_version               ├─ cleaned_at
                                └─ quality_checks (JSONB)          dim_customer
                                                                   dim_product
raw_events                       enriched_events                   dim_store
├─ id (PK)                      ├─ event_id (PK)                  dim_date
├─ raw_payload (JSONB)          ├─ event_type
├─ ingested_at                  ├─ customer_id                    agg_hourly_sales
└─ schema_version               ├─ enrichment_data (JSONB)        agg_daily_fraud
                                └─ processed_at
```

### Fraud Detection Rules (Rule-Based)

| Rule | Logic | Threshold | Flink Implementation |
|------|-------|-----------|---------------------|
| High Value | amount > customer_avg * 3 | 3x historical average | Keyed state per customer |
| Velocity | count(txn) in window > 5 | 5 transactions in 10 min | Sliding window + count |
| Geographic | distance(loc_a, loc_b) > 500km AND time < 1h | 500km/1h | CEP pattern matching |
| Time Anomaly | Transaction at unusual hour for customer | Outside 2σ of normal hours | Keyed state + statistics |
| Blacklist | merchant_id IN blacklist | Exact match | Broadcast state |

---

## Suggested Project Structure

```
streamflow-analytics/
├── README.md                              # Professional README with architecture diagrams
├── ARCHITECTURE.md                        # Detailed architecture decisions (ADRs)
├── Makefile                               # Developer convenience commands
├── pyproject.toml                         # Python project config (ruff, mypy, pytest)
├── .pre-commit-config.yaml                # Pre-commit hooks
├── .github/                               # CI/CD
│   └── workflows/
│       ├── ci.yaml                        # Lint + Test + Type check
│       └── deploy.yaml                    # Deploy to K3s
│
├── src/                                   # Main Python source
│   ├── __init__.py
│   ├── flink_jobs/                        # PyFlink streaming jobs
│   │   ├── __init__.py
│   │   ├── transaction_processor.py       # Kafka → Bronze
│   │   ├── fraud_detector.py              # Real-time fraud rules
│   │   ├── realtime_aggregator.py         # Windowed aggregations
│   │   └── common/                        # Shared Flink utilities
│   │       ├── __init__.py
│   │       ├── serialization.py           # Kafka serializers/deserializers
│   │       ├── schemas.py                 # Pydantic models for events
│   │       └── state.py                   # State management helpers
│   │
│   ├── dags/                              # Airflow DAGs
│   │   ├── __init__.py
│   │   ├── bronze_to_silver.py            # Bronze → Silver transforms
│   │   ├── silver_to_gold.py              # Silver → Gold star schema
│   │   ├── data_quality.py                # Data quality checks
│   │   └── maintenance.py                 # Cleanup + optimization
│   │
│   ├── generators/                        # Data generation
│   │   ├── __init__.py
│   │   ├── transaction_generator.py       # Realistic transaction events
│   │   ├── customer_generator.py          # Customer profiles
│   │   ├── store_generator.py             # Store data
│   │   ├── fraud_patterns.py              # Fraud injection patterns
│   │   └── kafka_producer.py              # Produce to Kafka topics
│   │
│   ├── models/                            # Shared data models (Pydantic)
│   │   ├── __init__.py
│   │   ├── transaction.py                 # Transaction event model
│   │   ├── customer.py                    # Customer model
│   │   ├── store.py                       # Store model
│   │   └── fraud_alert.py                 # Fraud alert model
│   │
│   └── utils/                             # Shared utilities
│       ├── __init__.py
│       ├── config.py                      # Configuration management
│       ├── logging.py                     # Structured logging setup
│       └── db.py                          # Database connection helpers
│
├── sql/                                   # SQL scripts by layer
│   ├── migrations/                        # Schema migrations (numbered)
│   │   ├── 001_create_bronze_schema.sql
│   │   ├── 002_create_silver_schema.sql
│   │   ├── 003_create_gold_schema.sql
│   │   └── 004_create_indexes.sql
│   ├── transforms/                        # Transformation queries
│   │   ├── bronze_to_silver.sql
│   │   └── silver_to_gold.sql
│   └── quality/                           # Data quality checks
│       └── quality_checks.sql
│
├── infra/                                 # Infrastructure as Code
│   ├── modules/                           # Terraform modules
│   │   ├── strimzi-kafka/                 # Kafka operator + cluster
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── flink-operator/                # Flink operator + deployments
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── cloudnativepg/                 # PostgreSQL operator + cluster
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   ├── airflow/                       # Airflow Helm release
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   └── monitoring/                    # kube-prometheus-stack
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   └── environments/                      # Terragrunt environments
│       ├── terragrunt.hcl                 # Root config (DRY)
│       ├── dev/
│       │   ├── terragrunt.hcl
│       │   ├── kafka/terragrunt.hcl
│       │   ├── flink/terragrunt.hcl
│       │   ├── postgresql/terragrunt.hcl
│       │   ├── airflow/terragrunt.hcl
│       │   └── monitoring/terragrunt.hcl
│       └── prod/
│           └── ... (same structure)
│
├── k8s/                                   # Kubernetes manifests (non-Terraform)
│   ├── namespaces.yaml                    # Namespace definitions
│   ├── kafka/                             # Strimzi CRDs
│   │   ├── kafka-cluster.yaml
│   │   ├── kafka-topics.yaml
│   │   └── kafka-users.yaml
│   ├── flink/                             # Flink CRDs
│   │   ├── transaction-processor.yaml
│   │   ├── fraud-detector.yaml
│   │   └── realtime-aggregator.yaml
│   └── monitoring/                        # Custom monitoring configs
│       ├── grafana-dashboards/
│       │   ├── pipeline-overview.json
│       │   ├── kafka-metrics.json
│       │   ├── flink-processing.json
│       │   └── fraud-monitoring.json
│       └── alerting-rules.yaml
│
├── scripts/                               # Automation scripts
│   ├── setup.sh                           # Initial cluster setup
│   ├── generate_events.py                 # Generate and produce events
│   ├── run_migrations.py                  # Execute SQL migrations
│   ├── verify_pipeline.py                 # End-to-end verification
│   └── seed_data.py                       # Seed reference data
│
├── tests/                                 # Test suites
│   ├── conftest.py                        # Shared fixtures
│   ├── __init__.py
│   ├── unit/                              # Unit tests
│   │   ├── __init__.py
│   │   ├── test_fraud_detector.py         # Fraud rules logic
│   │   ├── test_transaction_processor.py  # Processing logic
│   │   ├── test_generators.py             # Data generators
│   │   ├── test_models.py                 # Pydantic models
│   │   └── test_transforms.py            # SQL transform logic
│   ├── integration/                       # Integration tests
│   │   ├── __init__.py
│   │   ├── test_kafka_flink.py            # Kafka → Flink flow
│   │   └── test_flink_postgres.py         # Flink → PostgreSQL flow
│   └── e2e/                               # End-to-end tests
│       ├── __init__.py
│       └── test_full_pipeline.py          # Full pipeline validation
│
├── monitoring/                            # Monitoring configs
│   ├── prometheus/
│   │   └── additional-rules.yaml
│   └── grafana/
│       └── provisioning/
│           └── dashboards.yaml
│
├── config/                                # Application configs
│   ├── default.yaml                       # Default settings
│   ├── dev.yaml                           # Dev overrides
│   ├── prod.yaml                          # Prod overrides
│   └── fraud_rules.yaml                   # Fraud detection rules
│
├── docs/                                  # Documentation
│   ├── SETUP_GUIDE.md                     # Step-by-step setup
│   ├── STREAMING_ARCHITECTURE.md          # Streaming design details
│   ├── FRAUD_DETECTION.md                 # Fraud rules documentation
│   ├── RUNBOOK.md                         # Operations runbook
│   └── diagrams/                          # Architecture diagrams
│       ├── system-architecture.excalidraw
│       ├── data-flow.excalidraw
│       └── star-schema.excalidraw
│
└── .claude/                               # Claude Code ecosystem
    ├── CLAUDE.md                          # Project context (to be updated)
    ├── kb/                                # Knowledge Base
    │   ├── kafka/                         # To be created
    │   ├── flink/                         # To be created
    │   └── airflow/                       # To be created
    └── sdd/features/                      # This brainstorm + future phases
```

---

## Suggested Implementation Phases

### Phase 1: Foundation (Infrastructure + Schema)
**Priority:** CRITICAL - everything depends on this
- Terraform modules for all operators (Strimzi, Flink, CloudNativePG)
- Terragrunt environment structure (dev/prod)
- K3s namespace setup
- PostgreSQL Medallion schema (Bronze/Silver/Gold)
- SQL migrations system
- Pydantic data models
- Project config (pyproject.toml, ruff, mypy, pre-commit)

### Phase 2: Streaming Core (Kafka + Flink)
**Priority:** HIGH - the heart of the project
- Strimzi Kafka cluster + topic CRDs
- Flink Kubernetes Operator setup
- PyFlink job: transaction_processor (Kafka → Bronze)
- PyFlink job: realtime_aggregator (windowed metrics)
- Kafka serialization/deserialization
- Unit tests for processing logic

### Phase 3: Fraud Detection
**Priority:** HIGH - the differentiator
- PyFlink job: fraud_detector (rule-based)
- 5 fraud rules implementation (keyed state, windows, CEP)
- Fraud alerts topic + Bronze persistence
- fraud_rules.yaml configuration
- Unit tests for each rule
- Integration test: full fraud flow

### Phase 4: Batch Processing (Airflow)
**Priority:** MEDIUM - completes the Medallion pipeline
- Airflow Helm deployment with KubernetesExecutor
- DAG: bronze_to_silver (hourly transformations)
- DAG: silver_to_gold (star schema build)
- DAG: data_quality_checks (every 15 min)
- DAG: maintenance (daily cleanup)
- SQL transforms for each layer transition

### Phase 5: Data Generation
**Priority:** MEDIUM - makes the demo work
- Realistic transaction generator (based on Kaggle dataset distributions)
- Customer/Store/Product seed data
- Fraud pattern injection (configurable rate)
- Kafka producer script
- CLI interface for generating events

### Phase 6: Monitoring & Observability
**Priority:** MEDIUM - makes it production-grade
- kube-prometheus-stack deployment
- Custom Grafana dashboards (4 dashboards)
- AlertManager rules (consumer lag, job failures, fraud rate)
- Prometheus ServiceMonitors for Kafka, Flink, PostgreSQL
- Structured logging throughout

### Phase 7: CI/CD + Documentation
**Priority:** MEDIUM - polishes the portfolio
- GitHub Actions: CI (lint + test + typecheck)
- GitHub Actions: CD (deploy to K3s)
- README.md update with real screenshots/GIFs
- ARCHITECTURE.md with ADRs
- SETUP_GUIDE.md
- RUNBOOK.md

### Phase 8: Polish & Portfolio
**Priority:** LOW - the cherry on top
- Record demo video/GIF
- LinkedIn post draft
- Performance benchmarks
- Load testing results
- Final documentation review

---

## Suggested Requirements for /define

### Problem Statement (Draft)
Construir uma plataforma de streaming de dados em tempo real para detecção de fraude em e-commerce, deployada em K3s on-premise, usando arquitetura Medallion em PostgreSQL, com qualidade de código production-ready.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Tech leads / Hiring managers | Avaliar competência de Senior/Staff Data Engineer |
| Fellow engineers | Referência de arquitetura de streaming |
| Arthur (autor) | Demonstrar domínio de stack moderna de Data Engineering |

### Success Criteria (Draft)
- [ ] Pipeline end-to-end funcional: Gerador → Kafka → Flink → PostgreSQL → Grafana
- [ ] 5 regras de fraude implementadas e testadas
- [ ] Medallion architecture (Bronze/Silver/Gold) com transformações Airflow
- [ ] Toda infraestrutura provisionada via Terraform/Terragrunt
- [ ] Test coverage > 80%
- [ ] Zero warnings em ruff + mypy
- [ ] 4 dashboards Grafana funcionais
- [ ] Documentação completa (README, Architecture, Setup, Runbook)

### Constraints Identified
- Budget: $0 (todo open-source, K3s on-premise)
- K3s resources: limitados pela máquina física
- Sem cloud services (tudo on-premise)
- Python only (PyFlink, não Java/Scala)

### Out of Scope (Confirmed)
- Machine Learning models (sklearn, xgboost, etc.)
- Recomendações personalizadas
- Análise de churn / forecasting
- A/B testing framework
- Kafka Connect / Debezium CDC
- Multi-cloud deployment
- Authentication/authorization (simplifcado para portfólio)

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 6 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 8 |
| Validations Completed | 3 |
| Duration | ~30 min |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_STREAMFLOW_ANALYTICS.md`
