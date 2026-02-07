# DEFINE: StreamFlow Analytics

> Plataforma de streaming em tempo real para detecção de fraude em e-commerce, deployada em K3s on-premise com arquitetura Medallion e código production-ready.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | STREAMFLOW_ANALYTICS |
| **Date** | 2026-02-06 |
| **Author** | define-agent |
| **Status** | Ready for Design |
| **Clarity Score** | 15/15 |
| **Source** | BRAINSTORM_STREAMFLOW_ANALYTICS.md |

---

## Problem Statement

Arthur Maia Graf precisa de um projeto de portfólio que demonstre competência de **Senior/Staff Data Engineer** para tech leads e hiring managers. O projeto deve mostrar domínio real de streaming pipelines, Kubernetes operators, Infrastructure as Code, e qualidade de código production-grade — não apenas um tutorial funcional, mas um sistema que reflete decisões arquiteturais conscientes, trade-offs documentados, e engineering rigor.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| **Tech leads / Hiring managers** | Avaliadores técnicos | Precisam diferenciar candidatos senior de junior. Projetos genéricos não impressionam. Querem ver decisões arquiteturais, trade-offs, testes, IaC. |
| **Fellow Data Engineers** | Peers técnicos | Buscam referências de arquitetura de streaming real. Maioria dos projetos GitHub são tutoriais incompletos. |
| **Arthur (autor)** | Senior/Staff DE candidate | Precisa demonstrar domínio de stack moderna (Kafka, Flink, K8s, IaC) com evidência concreta, não apenas bullet points no LinkedIn. |

---

## Goals

| Priority | Goal | Measurable? |
|----------|------|-------------|
| **MUST** | Pipeline streaming end-to-end funcional: Generator → Kafka → Flink → PostgreSQL | Yes - dados fluem da geração até o Gold layer |
| **MUST** | 5 regras de fraude rule-based implementadas e testadas em PyFlink | Yes - cada regra com unit test |
| **MUST** | Medallion architecture (Bronze/Silver/Gold) com transformações batch via Airflow | Yes - 3 camadas com dados transitando |
| **MUST** | Toda infraestrutura provisionada via Terraform + Terragrunt no K3s | Yes - `terragrunt apply` provisiona tudo |
| **MUST** | Test coverage > 80% com pytest + ruff + mypy zero warnings | Yes - CI verifica automaticamente |
| **SHOULD** | 4 dashboards Grafana funcionais (Pipeline, Kafka, Flink, Fraud) | Yes - dashboards com dados reais |
| **SHOULD** | CI/CD via GitHub Actions (lint → test → typecheck → deploy) | Yes - pipeline passa em push |
| **SHOULD** | Documentação completa (README, Architecture ADRs, Setup Guide, Runbook) | Yes - docs existem e são navegáveis |
| **COULD** | Demo video/GIF para LinkedIn showcase | Yes - artefato existe |
| **COULD** | Performance benchmarks documentados (throughput, latência) | Yes - números publicados |

---

## Success Criteria

Measurable outcomes com números concretos:

- [ ] **SC-01:** Pipeline processa >= 100 eventos/segundo end-to-end (Generator → Kafka → Flink → Bronze)
- [ ] **SC-02:** Latência end-to-end < 30 segundos (evento gerado até persistido no Bronze)
- [ ] **SC-03:** 5 regras de fraude detectam corretamente >= 90% dos padrões de fraude injetados pelo gerador
- [ ] **SC-04:** Transformações Airflow (Bronze→Silver→Gold) completam em < 5 minutos para 100k registros
- [ ] **SC-05:** Test coverage >= 80% (unit + integration)
- [ ] **SC-06:** Zero warnings em `ruff check .` e `mypy src/`
- [ ] **SC-07:** `terragrunt run-all apply` provisiona toda infraestrutura do zero em < 15 minutos
- [ ] **SC-08:** 4 dashboards Grafana exibem métricas reais do pipeline em execução
- [ ] **SC-09:** README.md inclui diagramas de arquitetura, quick start, e demo evidence (screenshots/GIF)
- [ ] **SC-10:** Projeto funciona no K3s single-node com <= 4GB RAM alocados para StreamFlow

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Pipeline end-to-end (happy path) | Cluster K3s running com todos operators deployed | Generator produz 1000 transações para Kafka | Todas 1000 aparecem na tabela `bronze.raw_transactions` em < 30s |
| AT-002 | Fraud detection (high value) | Customer com média histórica de R$100 | Transação de R$500 é enviada (5x média) | Alerta de fraude é gerado no tópico `fraud-alerts` e persistido na tabela `bronze.raw_fraud_alerts` |
| AT-003 | Fraud detection (velocity) | Customer com atividade normal | 6 transações em 10 minutos (threshold = 5) | Alerta de velocidade é gerado com score > 0.8 |
| AT-004 | Medallion transformation | 1000 registros existem na tabela `bronze.raw_transactions` | DAG `bronze_to_silver` é executado | >= 950 registros aparecem em `silver.clean_transactions` (5% rejeição esperada por data quality) |
| AT-005 | Star schema build | Dados existem em Silver layer | DAG `silver_to_gold` é executado | `gold.fact_transactions` é populado com FKs válidas para todas dims |
| AT-006 | Data quality checks | Dados com problemas de qualidade injetados (nulls, duplicatas) | DAG `data_quality` é executado | Relatório identifica 100% dos problemas injetados |
| AT-007 | Infrastructure from scratch | Cluster K3s vazio (apenas kube-system) | `terragrunt run-all apply` executado na pasta `infra/environments/dev/` | Todos namespaces criados, operators instalados, CRDs aplicados, serviços rodando |
| AT-008 | Monitoring funcional | Pipeline em execução | Acessa Grafana via port-forward | 4 dashboards mostram métricas reais (não "No Data") |
| AT-009 | Generator com padrões realistas | Dataset Kaggle carregado como seed | Generator produz 10000 eventos | Distribuição de valores segue padrão log-normal similar ao dataset real |
| AT-010 | Recovery após restart | Pipeline em execução, dados fluindo | Pod do Flink job é deletado (`kubectl delete pod`) | Flink Operator recria o pod, job resume do último checkpoint, sem perda de dados |

---

## Out of Scope

Explicitamente **NÃO** incluído neste projeto:

| Item | Razão | Pode adicionar depois? |
|------|-------|----------------------|
| Machine Learning models (sklearn, xgboost, deep learning) | Escopo de Data Science, não Data Engineering. Rule-based é suficiente para demonstrar | Yes - Phase futura |
| Recomendações personalizadas | Feature de produto, não infraestrutura de dados | Yes |
| Análise de churn / Forecasting de vendas | Escopo de DS/Analytics | Yes |
| A/B testing framework | Over-engineering para portfólio | Yes |
| Kafka Connect / Debezium CDC | Adiciona complexidade sem valor proporcional para MVP | Yes - Extensão natural |
| Multi-cloud deployment | Budget $0, on-premise only | No (redesign completo) |
| Authentication/Authorization (RBAC, OAuth) | Simplificado para portfólio, não é o foco | Yes |
| Schema Registry (Confluent/Apicurio) | Nice-to-have mas adiciona complexidade, Pydantic cobre validação | Yes |
| Multi-node K3s cluster | Hardware limitado a 1 servidor | Yes (com mais hardware) |
| Real-time dashboards (Streamlit/Superset) | Grafana é suficiente para métricas. BI tool é scope creep | Yes |

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| **Hardware** | K3s single-node: 4 CPU, 9.7GB RAM, 598GB disk | Limita a 1 Kafka broker, 1 PG instance, 1 Flink TaskManager. Resource limits obrigatórios em todos pods |
| **Resources** | ~5.7GB RAM disponível, mas ~2-3GB já usados por outros workloads (mrhealth-db, platypus, portainer) | StreamFlow deve operar com <= 4GB RAM total alocado |
| **Budget** | $0 — zero custo de software ou cloud | Apenas ferramentas open-source. Sem licenças, sem SaaS, sem cloud managed services |
| **Language** | Python only (PyFlink) | Sem Java/Scala para Flink jobs. Limita algumas funcionalidades avançadas do Flink |
| **Network** | Servidor acessível via SSH (IP público) | Port-forward para acessar UIs (Grafana, Airflow). Sem ingress controller configurado |
| **Storage** | StorageClass: local-path (K3s default) | Sem replicação de storage. Dados perdidos se disco falhar. Aceitável para portfólio |
| **K3s Version** | v1.34.3+k3s1 | Versão recente, sem limitações conhecidas para operators |
| **Existing Workloads** | cert-manager, mrhealth-db (Airflow/Grafana/Prometheus), platypus-jobs, portainer | Não interferir nos namespaces existentes. Separação total via namespaces dedicados |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `src/` (Python), `infra/` (Terraform), `k8s/` (CRDs), `sql/` (migrations) | Múltiplos diretórios com responsabilidades claras |
| **KB Domains** | terraform, terragrunt (existentes) + kafka, flink, airflow (a criar) | Criar KBs para Kafka/Flink/Airflow durante /build |
| **IaC Impact** | Novos recursos: 5 namespaces, 3 operators, 2 Helm releases, CRDs | Terraform modules + Terragrunt environments (dev) |

**Cluster Resources já disponíveis:**

| Recurso | Status | Namespace |
|---------|--------|-----------|
| cert-manager | Instalado | cert-manager |
| Helm | Instalado | - |
| kubectl | Configurado | - |
| local-path StorageClass | Default | kube-system |
| metrics-server | Instalado | kube-system |

**Operators a instalar (via Terraform):**

| Operator | CRDs | Namespace Target |
|----------|------|-----------------|
| Strimzi (Kafka) | Kafka, KafkaTopic, KafkaUser | streamflow-kafka |
| Flink Kubernetes Operator | FlinkDeployment | streamflow-processing |
| CloudNativePG | Cluster, Backup, ScheduledBackup | streamflow-data |

**Helm Releases a instalar (via Terraform):**

| Chart | Namespace Target |
|-------|-----------------|
| apache-airflow/airflow | streamflow-orchestration |
| prometheus-community/kube-prometheus-stack | streamflow-monitoring |

---

## Resource Budget (K3s)

Allocation plan para caber em ~4GB RAM:

| Component | Namespace | CPU Request | CPU Limit | RAM Request | RAM Limit |
|-----------|-----------|-------------|-----------|-------------|-----------|
| Strimzi Operator | streamflow-kafka | 100m | 200m | 128Mi | 256Mi |
| Kafka Broker (1x, KRaft) | streamflow-kafka | 200m | 500m | 512Mi | 768Mi |
| Flink Operator | streamflow-processing | 100m | 200m | 128Mi | 256Mi |
| Flink JobManager | streamflow-processing | 100m | 300m | 256Mi | 512Mi |
| Flink TaskManager (1x, 2 slots) | streamflow-processing | 200m | 500m | 512Mi | 768Mi |
| CloudNativePG Operator | streamflow-data | 50m | 100m | 64Mi | 128Mi |
| PostgreSQL (1x, no replica) | streamflow-data | 200m | 500m | 256Mi | 512Mi |
| Airflow Webserver | streamflow-orchestration | 100m | 200m | 256Mi | 384Mi |
| Airflow Scheduler | streamflow-orchestration | 100m | 200m | 256Mi | 384Mi |
| Prometheus | streamflow-monitoring | 100m | 200m | 256Mi | 384Mi |
| Grafana | streamflow-monitoring | 50m | 100m | 128Mi | 192Mi |
| **TOTAL** | | **1300m** | **3000m** | **2752Mi** | **4544Mi** |

**Nota:** Total request ~2.7GB RAM, total limit ~4.4GB. Cabe no cluster com margem para burst.

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | K3s single-node suporta 5 operators + workloads simultaneamente com 4GB alocados | Precisaria reduzir componentes ou aumentar RAM do servidor | [x] Parcialmente - cluster já roda workloads similares (mrhealth-db) |
| A-002 | local-path StorageClass é suficiente para PVCs de Kafka e PostgreSQL | Precisaria de StorageClass mais robusto (Longhorn, OpenEBS) | [ ] A validar durante Build |
| A-003 | PyFlink 1.18+ suporta todas as features necessárias (keyed state, windows, CEP) | Precisaria de Java/Scala para funcionalidades avançadas | [x] Documentação confirma suporte |
| A-004 | Strimzi suporta KRaft mode single-broker em K3s | Precisaria de ZooKeeper (mais recursos) | [ ] A validar durante Build |
| A-005 | Flink Kubernetes Operator funciona em K3s (não apenas EKS/GKE) | Precisaria de deployment manual | [ ] A validar durante Build |
| A-006 | 100 eventos/segundo é atingível com os resources alocados | Precisaria otimizar ou reduzir throughput target | [ ] A validar durante Build |
| A-007 | Dataset Kaggle Credit Card Fraud é suficiente para calibrar gerador realista | Precisaria de datasets adicionais | [x] Dataset tem 284k amostras com distribuições reais |

---

## Technology Stack (Definitive)

| Layer | Technology | Version | Purpose | K8s Deployment |
|-------|-----------|---------|---------|----------------|
| Event Streaming | Apache Kafka | 3.7+ | Event backbone, message durability, replay | Strimzi Operator (KRaft, 1 broker) |
| Stream Processing | Apache Flink | 1.18+ | Real-time processing, fraud detection, aggregations | Flink K8s Operator (1 JM + 1 TM) |
| Batch Orchestration | Apache Airflow | 2.8+ | DAG scheduling, Bronze→Silver→Gold transforms | Helm chart, LocalExecutor |
| Data Warehouse | PostgreSQL | 16+ | Medallion architecture, ACID, full SQL | CloudNativePG Operator (1 instance) |
| Monitoring | Prometheus + Grafana | Latest | Metrics collection, dashboards, alerting | kube-prometheus-stack Helm |
| IaC | Terraform + Terragrunt | 1.7+ / 0.55+ | Infrastructure provisioning, DRY configs | N/A (runs from local machine) |
| Language | Python | 3.11+ | PyFlink jobs, DAGs, generators, scripts | Container images |
| Data Models | Pydantic | 2.x | Schema validation, serialization | Python library |
| Testing | pytest + ruff + mypy | Latest | Unit/integration tests, linting, type checking | CI pipeline |
| CI/CD | GitHub Actions | N/A | Automated lint, test, typecheck, deploy | GitHub-hosted runners |

---

## Data Architecture (Medallion in PostgreSQL)

### Bronze Layer (Raw, Immutable)
**Schema:** `bronze`
**Purpose:** Landing zone para dados brutos do Kafka. Imutável, append-only.

| Table | Source | Key Columns | Notes |
|-------|--------|-------------|-------|
| `raw_transactions` | Flink (Kafka consumer) | id, kafka_offset, raw_payload (JSONB), ingested_at | Append-only, partitioned by ingested_at |
| `raw_fraud_alerts` | Flink (fraud detector) | id, alert_type, raw_payload (JSONB), detected_at | Fraud events from real-time detection |

### Silver Layer (Cleaned, Enriched)
**Schema:** `silver`
**Purpose:** Dados limpos, validados, enriquecidos. Deduplicados.

| Table | Source | Key Columns | Notes |
|-------|--------|-------------|-------|
| `clean_transactions` | Airflow DAG (from bronze) | transaction_id, customer_id, store_id, amount, fraud_score, is_valid | Validated, nulls handled, types enforced |
| `customers` | Seed data + enrichment | customer_id, name, email, avg_transaction, risk_profile | Reference data enriched over time |
| `stores` | Seed data | store_id, name, city, state, category | Static reference data |
| `products` | Seed data | product_id, name, category, price | Static reference data |

### Gold Layer (Business-Ready, Star Schema)
**Schema:** `gold`
**Purpose:** Star schema otimizado para analytics. Dims + Facts + Aggs.

| Table | Type | Key Columns | Notes |
|-------|------|-------------|-------|
| `dim_customer` | Dimension (SCD Type 1) | customer_key, customer_id, name, risk_profile | Slowly changing |
| `dim_store` | Dimension | store_key, store_id, name, city, state | Static |
| `dim_product` | Dimension | product_key, product_id, name, category | Static |
| `dim_date` | Dimension | date_key, date, day_of_week, month, quarter, year | Pre-populated |
| `fact_transactions` | Fact | transaction_key, date_key, customer_key, store_key, product_key, amount, fraud_flag | Grain: 1 transaction |
| `fact_fraud_alerts` | Fact | alert_key, date_key, customer_key, alert_type, fraud_score, rule_triggered | Grain: 1 alert |
| `agg_hourly_sales` | Aggregate | hour_key, store_key, total_amount, transaction_count, avg_amount | Pre-computed hourly |
| `agg_daily_fraud` | Aggregate | date_key, total_alerts, fraud_rate, top_rule, avg_score | Pre-computed daily |

---

## Fraud Detection Rules (Definitive)

| ID | Rule | Logic | Threshold | Flink Technique | Priority |
|----|------|-------|-----------|-----------------|----------|
| FR-001 | High Value | `amount > customer_avg_amount * multiplier` | 3x historical avg | Keyed state per customer_id | MUST |
| FR-002 | Velocity | `count(txn) in sliding_window > max_count` | 5 transactions in 10 min | Sliding window + ProcessFunction | MUST |
| FR-003 | Geographic Anomaly | `haversine(last_loc, curr_loc) > max_dist AND time_delta < max_time` | 500km in < 1 hour | Keyed state with last location | MUST |
| FR-004 | Time Anomaly | `hour_of_day outside customer_normal_range` | Outside 2σ of normal hours | Keyed state with hour distribution | SHOULD |
| FR-005 | Blacklist Match | `merchant_id IN blacklist OR region IN blacklist` | Exact match | Broadcast state (refreshable) | MUST |

**Scoring:** Each rule produces a score 0.0-1.0. Combined score = weighted average. Alert if combined_score > 0.7.

---

## Kafka Topics (Definitive)

| Topic | Partitions | Retention | Producers | Consumers | Purpose |
|-------|-----------|-----------|-----------|-----------|---------|
| `transactions.raw` | 3 | 7 days | Data Generator | Flink (transaction_processor, fraud_detector) | Raw transaction events |
| `fraud.alerts` | 1 | 30 days | Flink (fraud_detector) | Flink (persistence), Monitoring | Fraud alert events |
| `metrics.realtime` | 1 | 1 day | Flink (realtime_aggregator) | Monitoring | Real-time aggregated metrics |

---

## Airflow DAGs (Definitive)

| DAG | Schedule | Depends On | Actions | SLA |
|-----|----------|------------|---------|-----|
| `bronze_to_silver` | `@hourly` | Bronze tables have new data | Validate, clean, deduplicate, enrich → Silver tables | 5 min |
| `silver_to_gold` | `@hourly` (after bronze_to_silver) | Silver tables updated | Build dims (SCD), populate facts, compute aggregates → Gold tables | 5 min |
| `data_quality` | `*/15 * * * *` | Bronze + Silver tables | Null checks, range validation, freshness checks, duplicate detection | 2 min |
| `maintenance` | `0 3 * * *` | None | Vacuum analyze, partition pruning, old data cleanup | 10 min |

---

## Implementation Phases (Definitive)

### Phase 1: Foundation
**Deliverables:**
- `pyproject.toml` configured (ruff, mypy, pytest, dependencies)
- `.pre-commit-config.yaml` (ruff, mypy, trailing whitespace)
- `Makefile` (lint, test, typecheck, format commands)
- `src/models/` — Pydantic models (Transaction, Customer, Store, FraudAlert)
- `src/utils/` — Config, logging, database helpers
- `sql/migrations/` — Bronze, Silver, Gold schemas
- `config/` — YAML configs (default, dev, fraud_rules)
- `tests/unit/test_models.py` — Model validation tests
- `infra/modules/` — Terraform modules skeleton
- `infra/environments/` — Terragrunt structure (dev)

### Phase 2: Infrastructure (K3s)
**Deliverables:**
- `infra/modules/strimzi-kafka/` — Strimzi operator + Kafka cluster + topics
- `infra/modules/flink-operator/` — Flink K8s Operator
- `infra/modules/cloudnativepg/` — CloudNativePG + PostgreSQL cluster
- `infra/modules/airflow/` — Airflow Helm release
- `infra/modules/monitoring/` — kube-prometheus-stack
- `infra/environments/dev/` — All Terragrunt configs
- `scripts/setup.sh` — Initial cluster bootstrapping
- AT-007 passes (infra from scratch)

### Phase 3: Streaming Core
**Deliverables:**
- `src/flink_jobs/transaction_processor.py` — Kafka → validate → Bronze
- `src/flink_jobs/common/serialization.py` — Kafka SerDe
- `src/flink_jobs/common/schemas.py` — Flink type mappings
- `k8s/kafka/kafka-topics.yaml` — Strimzi KafkaTopic CRDs
- `k8s/flink/transaction-processor.yaml` — FlinkDeployment CRD
- `tests/unit/test_transaction_processor.py`
- AT-001 passes (end-to-end pipeline)

### Phase 4: Fraud Detection
**Deliverables:**
- `src/flink_jobs/fraud_detector.py` — 5 fraud rules
- `config/fraud_rules.yaml` — Rule thresholds (configurable)
- `k8s/flink/fraud-detector.yaml` — FlinkDeployment CRD
- `tests/unit/test_fraud_detector.py` — Per-rule tests
- `tests/integration/test_fraud_flow.py`
- AT-002, AT-003 pass (fraud detection)

### Phase 5: Batch Processing
**Deliverables:**
- `src/dags/bronze_to_silver.py` — Airflow DAG
- `src/dags/silver_to_gold.py` — Airflow DAG
- `src/dags/data_quality.py` — Airflow DAG
- `src/dags/maintenance.py` — Airflow DAG
- `sql/transforms/bronze_to_silver.sql`
- `sql/transforms/silver_to_gold.sql`
- `sql/quality/quality_checks.sql`
- AT-004, AT-005, AT-006 pass (Medallion pipeline)

### Phase 6: Data Generation
**Deliverables:**
- `src/generators/transaction_generator.py` — Realistic events
- `src/generators/fraud_patterns.py` — Fraud injection
- `src/generators/kafka_producer.py` — Produce to Kafka
- `scripts/generate_events.py` — CLI wrapper
- `scripts/seed_data.py` — Seed reference data
- `tests/unit/test_generators.py`
- AT-009 passes (realistic data)

### Phase 7: Monitoring & Observability
**Deliverables:**
- `k8s/monitoring/grafana-dashboards/` — 4 JSON dashboards
- `k8s/monitoring/alerting-rules.yaml` — AlertManager rules
- Prometheus ServiceMonitors for Kafka, Flink, PostgreSQL
- Structured logging in all Python code
- AT-008 passes (monitoring functional)

### Phase 8: CI/CD + Documentation + Polish
**Deliverables:**
- `.github/workflows/ci.yaml` — Lint + Test + Typecheck
- `.github/workflows/deploy.yaml` — Deploy to K3s
- `README.md` — Professional with diagrams and demo evidence
- `ARCHITECTURE.md` — ADRs for all key decisions
- `docs/SETUP_GUIDE.md` — Step-by-step
- `docs/RUNBOOK.md` — Operations guide
- `docs/FRAUD_DETECTION.md` — Rules documentation
- SC-09 passes (documentation complete)

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Crystal clear: portfolio project demonstrating Senior/Staff DE competence via streaming platform |
| Users | 3 | Three personas identified with specific pain points. Context of portfolio makes users well-defined |
| Goals | 3 | MoSCoW prioritized, all measurable. 6 MUST, 2 SHOULD, 2 COULD |
| Success | 3 | 10 success criteria with specific numbers (100 evt/s, 30s latency, 80% coverage, etc.) |
| Scope | 3 | 10 explicit out-of-scope items with reasoning. YAGNI applied systematically |
| **Total** | **15/15** | |

---

## Open Questions

None — ready for Design.

All major questions were resolved during BRAINSTORM phase:
- Architecture approach: Operator-native (confirmed)
- Deployment: K3s only (confirmed)
- Data source: Kaggle + generator (confirmed)
- Quality: Full stack (confirmed)
- YAGNI: 8 features removed (confirmed)
- Server specs: Verified via SSH (4 CPU, 9.7GB RAM, 598GB disk)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-06 | define-agent | Initial version from BRAINSTORM_STREAMFLOW_ANALYTICS.md |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_STREAMFLOW_ANALYTICS.md`
