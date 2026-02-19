# BRAINSTORM: End-to-End Production Deploy + dbt Integration

> Upgrade StreamFlow Analytics from portfolio code to fully running production platform

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | E2E_PRODUCTION |
| **Date** | 2026-02-18 |
| **Author** | brainstorm-agent + the-planner |
| **Status** | Ready for Define |

---

## Initial Idea

**Raw Input:** "Faça um planejamento para ficar 15/15 para um staff engineer, deve funcionar de ponta a ponta, use o dbt dentro do Airflow como extensão dentro do Airflow"

**Context Gathered:**
- Project has 263 passing tests, mypy strict, zero ruff warnings — code quality is 10/10
- Critical deployment gaps: no Dockerfiles, no container images, no JAR build pipeline
- DAGs use raw PostgresOperator with SQL files — no dbt, no lineage, no schema tests
- K3s server available (15.235.61.251, 4 cores, ~5.7GB free RAM, 527GB disk)
- All Terraform modules exist but Flink jobs cannot start (missing container image + Python code)
- SQL transforms exist in `sql/transforms/` and `sql/quality/` — ready to migrate to dbt

**Technical Context Observed (for Define):**

| Aspect | Observation | Implication |
|--------|-------------|-------------|
| Likely Location | `dbt/`, `docker/`, `.github/workflows/`, `src/dags/` | New directories + modified DAGs |
| Relevant KB Domains | dbt, cosmos, docker, k3s, airflow | Patterns to consult |
| IaC Patterns | Existing Terraform modules in `infra/modules/` | Extend for dbt + images |

---

## Discovery Questions & Answers

| # | Question | Answer | Impact |
|---|----------|--------|--------|
| 1 | Deploy real no K3s ou apenas deployable com docs? | **Rodar de verdade** no K3s | Precisamos de Dockerfiles, registry, deploy scripts funcionais, smoke tests reais |
| 2 | dbt substitui todos os SQLs ou apenas Gold? | **dbt substitui TUDO** (Bronze→Silver, Silver→Gold, quality checks) | Migrar 18 SQL files para modelos dbt, usar Cosmos no Airflow |
| 3 | Container registry: ghcr.io ou local K3s? | **Registry local K3s** | Usar `k3s ctr images import` para single-node, sem dependência externa |
| 4 | Flink: PyFlink puro, JAR wrapper, ou Python puro? | **PyFlink puro + Docker** | Dockerfile customizado com Python + PyFlink, sem JAR Java |
| 5 | Resources: minimal, full stack, ou híbrido? | **Minimal** (single-replica, sem Prometheus/Grafana) | Libera ~2GB RAM, monitoring via Airflow UI + logs |

---

## Sample Data Inventory

| Type | Location | Count | Notes |
|------|----------|-------|-------|
| Input SQL transforms | `sql/transforms/*.sql` | 6 | Bronze→Silver + Gold transforms |
| Gold transforms | `sql/transforms/gold/*.sql` | 6 | Dimensions, facts, aggregates |
| Quality checks | `sql/quality/*.sql` | 4 | Null rate, duplicates, freshness, amounts |
| Migrations (schema DDL) | `sql/migrations/*.sql` | 4 | Bronze, Silver, Gold schemas + indexes |
| Config | `config/default.yaml` | 1 | Kafka, PG, Flink, fraud rules config |
| K8s manifests | `k8s/**/*.yaml` | 11 | Flink, Kafka, security, monitoring |
| Terraform modules | `infra/modules/` | 6 | Complete IaC for all operators |

**How samples will be used:**
- SQL transforms → Direct migration to dbt models
- Quality checks → dbt singular tests + schema tests
- Schema DDL → dbt sources definition
- Config → Docker ENV + dbt profiles

---

## Approaches Explored

### Approach A: Astronomer Cosmos + dbt-core + Docker Build Pipeline ⭐ Recommended

**Description:** Use `astronomer-cosmos` to natively integrate dbt inside Airflow DAGs. Each dbt model becomes an Airflow task with full visibility. Build custom Docker images for Flink (PyFlink) and Airflow (with dbt + cosmos). Use `k3s ctr images import` for local registry.

**Pros:**
- Most modern dbt+Airflow integration (used by Astronomer, major companies)
- Each dbt model visible as Airflow task → full lineage in Airflow UI
- dbt tests run as Airflow tasks → native alerting on failures
- PyFlink Docker image is straightforward (no JAR complexity)
- Local K3s registry is simplest for single-node ($0 cost)
- Fully GitOps: code push → CI builds image → deploy imports to K3s

**Cons:**
- Cosmos adds a dependency (~15MB)
- Airflow image becomes heavier (dbt + cosmos + dbt-postgres)
- Need to manage image versions in K8s manifests

**Why Recommended:** Maximum Staff-level signal. Shows mastery of dbt, Airflow orchestration, containerization, and K8s deployment. End-to-end verifiable pipeline.

---

### Approach B: BashOperator + dbt CLI

**Description:** Run `dbt run` and `dbt test` via BashOperator in Airflow. Simpler integration, less visibility.

**Pros:**
- Simpler, fewer dependencies
- dbt CLI is well-documented

**Cons:**
- No per-model visibility in Airflow UI (one big task)
- No automatic dependency detection
- Less impressive for Staff portfolio
- Manual retry logic needed per model

---

### Approach C: dbt + Custom Python Operator

**Description:** Write custom Airflow Operator that wraps dbt Python API.

**Pros:**
- Full control over execution
- Can add custom logging/metrics

**Cons:**
- Reinventing Cosmos (which already solves this)
- More code to maintain
- Less community adoption / recognition

---

## Selected Approach

| Attribute | Value |
|-----------|-------|
| **Chosen** | Approach A: Astronomer Cosmos + dbt-core + Docker Build Pipeline |
| **User Confirmation** | 2026-02-18 |
| **Reasoning** | Maximum Staff signal, modern patterns, full Airflow visibility, end-to-end verifiable |

---

## Key Decisions Made

| # | Decision | Rationale | Alternative Rejected |
|---|----------|-----------|----------------------|
| 1 | dbt replaces ALL SQL transforms | Full dbt coverage shows mastery; partial migration looks incomplete | dbt only for Gold layer |
| 2 | Astronomer Cosmos for Airflow integration | Industry standard, per-model Airflow tasks, auto-dependency graph | BashOperator (no visibility) |
| 3 | PyFlink pure Docker (no JAR) | Python-native, simpler build, no Maven/Gradle complexity | JAR wrapper with PythonDriver |
| 4 | K3s local registry via `ctr images import` | Simplest for single-node, no external dependencies | ghcr.io (adds network dependency) |
| 5 | Minimal resources (no Prometheus/Grafana) | 5.7GB RAM constraint, monitoring via Airflow UI + logs | Full monitoring stack |
| 6 | Multi-stage Docker builds | Smaller images, security best practice, shows DevOps maturity | Single-stage builds |

---

## Features Removed (YAGNI)

| Feature Suggested | Reason Removed | Can Add Later? |
|-------------------|----------------|----------------|
| Grafana dashboards | RAM constraint, monitoring via Airflow UI is sufficient | Yes |
| Prometheus ServiceMonitors (active scraping) | No Prometheus pod to scrape | Yes |
| dbt exposures | Nice-to-have, not needed for functioning pipeline | Yes |
| elementary data observability | Overkill for portfolio project, dbt tests are sufficient | Yes |
| Multi-environment dbt profiles (dev/staging/prod) | Single K3s node, one environment | Yes |
| dbt Cloud integration | Costs money, $0 budget | No |
| Helm chart packaging | Raw manifests + Kustomize is sufficient | Yes |

---

## Incremental Validations

| Section | Presented | User Feedback | Adjusted? |
|---------|-----------|---------------|-----------|
| Deploy goal (real vs deployable) | ✅ | Rodar de verdade | No |
| dbt scope (full vs partial) | ✅ | Full replacement | No |
| Architecture (Cosmos + pipeline flow) | ✅ | Aprovado | No |
| Flink approach (PyFlink vs JAR) | ✅ | PyFlink puro | No |
| Resource budget (minimal) | ✅ | Minimal aprovado | No |

---

## Implementation Plan: 5 Phases

### Phase 1: Containerization Foundation (Deploy Unblock)

**Goal:** Create Docker images and get Flink + Generator running on K3s

**Deliverables:**
1. `docker/flink/Dockerfile` — Multi-stage: Flink 1.20 + Python 3.12 + PyFlink + scikit-learn + source code
2. `docker/generator/Dockerfile` — Python 3.12 + confluent-kafka + generators
3. `docker/airflow/Dockerfile` — Airflow 2.x + dbt-core + dbt-postgres + cosmos
4. `scripts/build_images.sh` — Build all images locally
5. `scripts/import_images.sh` — `k3s ctr images import` for local registry
6. Update `k8s/flink/*.yaml` — Change image + remove JAR reference, use Python app mode
7. Update `.github/workflows/ci.yaml` — Add Docker build job

**Success Criteria:**
- [ ] `docker build` succeeds for all 3 images
- [ ] `k3s ctr images import` loads images on server
- [ ] Flink FlinkDeployment starts and job enters RUNNING state
- [ ] Generator produces events to Kafka

---

### Phase 2: dbt Project (Transform Layer)

**Goal:** Migrate all SQL transforms to dbt models with tests

**Deliverables:**
1. `dbt/dbt_project.yml` — Project configuration
2. `dbt/profiles.yml` — PostgreSQL connection
3. `dbt/packages.yml` — dbt-utils, dbt-expectations
4. `dbt/models/staging/` — Bronze → Silver transforms (stg_transactions, stg_fraud_alerts)
5. `dbt/models/staging/_staging__sources.yml` — Source definitions
6. `dbt/models/intermediate/` — Customer stats enrichment
7. `dbt/models/marts/` — Gold layer (dim_customer, dim_store, fct_transactions, fct_fraud_alerts, agg_hourly_sales, agg_daily_fraud)
8. `dbt/models/marts/_marts__schema.yml` — Schema tests (not_null, unique, accepted_values)
9. `dbt/tests/` — Singular tests (freshness, amounts, null_rate, duplicates)
10. `dbt/macros/generate_schema_name.sql` — Custom schema routing (staging→silver, marts→gold)

**Success Criteria:**
- [ ] `dbt run` succeeds against local/test PostgreSQL
- [ ] `dbt test` passes all schema + singular tests
- [ ] `dbt docs generate` produces lineage graph
- [ ] All 18 existing SQL files have dbt equivalents

---

### Phase 3: Airflow + Cosmos DAGs (Orchestration)

**Goal:** Replace PostgresOperator DAGs with Cosmos DbtTaskGroup DAGs

**Deliverables:**
1. `src/dags/dbt_staging.py` — Cosmos DbtTaskGroup for staging models
2. `src/dags/dbt_marts.py` — Cosmos DbtTaskGroup for marts models
3. `src/dags/dbt_quality.py` — Cosmos DbtTestLocalOperator for tests
4. `src/dags/maintenance.py` — Keep as-is (VACUUM doesn't need dbt)
5. Airflow Helm values update — DAG git-sync, connection provisioning
6. Remove old DAGs: `bronze_to_silver.py`, `silver_to_gold.py`, `data_quality.py`
7. Tests for new DAGs (DAG import tests, structure validation)

**Success Criteria:**
- [ ] Airflow UI shows dbt tasks as individual nodes
- [ ] dbt_staging DAG runs successfully on schedule
- [ ] dbt_marts DAG waits for staging, then runs
- [ ] dbt_quality DAG runs tests and alerts on failure
- [ ] DAGs auto-sync from git to Airflow

---

### Phase 4: End-to-End Integration (Wire Everything)

**Goal:** Full pipeline running on K3s, data flowing from generator to Gold layer

**Deliverables:**
1. Updated `scripts/deploy.sh` v2 — Includes image build + import + full deploy
2. `scripts/setup_k3s.sh` — K3s registry config, namespace setup
3. Airflow connection provisioning (via Helm init container or env var)
4. Generator as K8s CronJob or Deployment (not local script)
5. ML model packaging in Flink Docker image
6. Full smoke test: data visible in Gold schema after pipeline run
7. `scripts/demo.sh` — One-command demo (deploy + generate + wait + verify)

**Success Criteria:**
- [ ] `./scripts/demo.sh` runs end-to-end without manual intervention
- [ ] Data visible in `gold.dim_customer`, `gold.fct_transactions`, `gold.agg_hourly_sales`
- [ ] Flink jobs in RUNNING state
- [ ] Airflow DAGs triggered and succeeding
- [ ] Zero pod crashes after 10 minutes

---

### Phase 5: Staff Polish (15/15 Finish)

**Goal:** Documentation, ADRs, and demo-readiness for interviews/LinkedIn

**Deliverables:**
1. Updated `README.md` — New architecture diagram with dbt layer, demo instructions
2. `docs/adr/013-dbt-over-raw-sql.md` — ADR for dbt decision
3. `docs/adr/014-cosmos-airflow-integration.md` — ADR for Cosmos
4. `docs/adr/015-pyflink-docker-no-jar.md` — ADR for PyFlink approach
5. Updated `docs/SETUP_GUIDE.md` — Real deploy instructions
6. dbt docs static site (generated HTML for GitHub Pages or local)
7. Screenshots/GIFs of: Airflow DAG graph, dbt lineage, Flink dashboard, Gold query results
8. CI/CD: All 5 jobs green (lint, typecheck, test, security, k8s-validate)
9. Update test suite for new dbt DAGs and Docker components

**Success Criteria:**
- [ ] README has "Quick Start" that works in <15 minutes
- [ ] Architecture diagram shows complete data flow
- [ ] ADRs document all major decisions
- [ ] dbt lineage graph available
- [ ] All CI checks green
- [ ] Project tells a compelling Staff Engineer story

---

## Scoring Model: 15/15

| Dimension | Current | After Upgrade | Max |
|-----------|---------|---------------|-----|
| **Architecture & Design** | 3/3 | 3/3 | 3 |
| **Code Quality & Testing** | 3/3 | 3/3 | 3 |
| **Data Engineering (dbt + Medallion)** | 1/3 | 3/3 | 3 |
| **DevOps & Platform (Docker + K8s + CI/CD)** | 1/3 | 3/3 | 3 |
| **Production Readiness (E2E + Monitoring)** | 0/3 | 3/3 | 3 |
| **TOTAL** | **8/15** | **15/15** | **15** |

---

## Suggested Requirements for /define

### Problem Statement (Draft)
StreamFlow Analytics has excellent code quality but cannot deploy end-to-end. Adding dbt integration and containerization completes the Staff Engineer story.

### Target Users (Draft)
| User | Pain Point |
|------|------------|
| Hiring Manager | Cannot verify claims of "production K8s streaming platform" |
| Technical Interviewer | Wants to see real dbt lineage, real Airflow DAGs, real data flow |
| Arthur (author) | Needs portfolio that runs, not just compiles |

### Success Criteria (Draft)
- [ ] `./scripts/demo.sh` deploys and runs full pipeline in <15 minutes
- [ ] dbt lineage graph shows Bronze → Silver → Gold flow
- [ ] Airflow UI shows dbt tasks as individual Cosmos nodes
- [ ] Gold layer has queryable fraud analytics data
- [ ] All CI checks pass (lint, typecheck, test, security, k8s-validate)
- [ ] README Quick Start works for a fresh clone

### Constraints Identified
- K3s server: 4 cores, ~5.7GB free RAM, 527GB disk
- Budget: $0 (all open-source)
- Single-node K3s (no HA)
- No Prometheus/Grafana (RAM constraint)

### Out of Scope (Confirmed)
- Grafana dashboards
- dbt Cloud
- elementary observability
- Multi-environment deployments
- Helm chart packaging
- HA / multi-node K3s

---

## Session Summary

| Metric | Value |
|--------|-------|
| Questions Asked | 5 |
| Approaches Explored | 3 |
| Features Removed (YAGNI) | 7 |
| Validations Completed | 5 |
| Phases Planned | 5 |

---

## Next Step

**Ready for:** `/define .claude/sdd/features/BRAINSTORM_E2E_PRODUCTION.md`
