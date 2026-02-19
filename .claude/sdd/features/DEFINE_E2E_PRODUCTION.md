# DEFINE: End-to-End Production Deploy + dbt Integration

> Upgrade StreamFlow Analytics to a fully running production platform with dbt inside Airflow, containerized services on K3s, and 15/15 Staff Engineer portfolio readiness.

## Metadata

| Attribute | Value |
|-----------|-------|
| **Feature** | E2E_PRODUCTION |
| **Date** | 2026-02-18 |
| **Author** | define-agent |
| **Status** | Ready for Design |
| **Clarity Score** | 14/15 |
| **Brainstorm** | [BRAINSTORM_E2E_PRODUCTION.md](BRAINSTORM_E2E_PRODUCTION.md) |

---

## Problem Statement

StreamFlow Analytics has excellent code quality (263 tests, mypy strict, zero warnings) but **cannot deploy end-to-end**: no Dockerfiles exist, Flink jobs reference a nonexistent JAR, DAGs aren't provisioned to Airflow, and SQL transforms have schema mismatches. Adding dbt integration and containerization completes the Staff Engineer story and makes the project verifiably functional.

---

## Target Users

| User | Role | Pain Point |
|------|------|------------|
| Hiring Manager | Evaluating candidate | Cannot verify "production K8s streaming platform" claim — code doesn't run |
| Technical Interviewer | Deep-dive review | No dbt lineage, no real data flow, no live demo possible |
| Arthur (author) | Portfolio owner | Needs project that runs end-to-end, not just compiles |

---

## Goals

| Priority | Goal |
|----------|------|
| **MUST** | Flink jobs run on K3s with custom Docker image (PyFlink + Python code) |
| **MUST** | dbt replaces ALL SQL transforms (Bronze→Silver, Silver→Gold, quality checks) |
| **MUST** | Airflow orchestrates dbt via Astronomer Cosmos (DbtTaskGroup) |
| **MUST** | Full pipeline works: Generator → Kafka → Flink → Bronze (PG) → dbt → Silver → Gold |
| **MUST** | `./scripts/demo.sh` deploys and runs everything in <15 minutes |
| **SHOULD** | CI/CD builds Docker images and validates dbt |
| **SHOULD** | dbt docs generate produces lineage graph |
| **SHOULD** | ADRs document dbt, Cosmos, and PyFlink decisions |
| **COULD** | Screenshots/GIFs for README demo section |

---

## Success Criteria

- [ ] All 3 Flink FlinkDeployments enter RUNNING state on K3s
- [ ] `dbt run` succeeds for all staging + intermediate + marts models
- [ ] `dbt test` passes all schema tests + singular tests (>15 tests)
- [ ] Airflow UI shows Cosmos DbtTaskGroup with per-model tasks
- [ ] Gold schema has queryable data: `SELECT COUNT(*) FROM gold.fct_transactions` > 0
- [ ] `dbt docs generate` produces lineage graph with >10 nodes
- [ ] `./scripts/demo.sh` completes without manual intervention
- [ ] All CI checks pass (lint, typecheck, test, security, k8s-validate)
- [ ] Zero pod crashes after 10 minutes of running
- [ ] 263+ existing tests still pass (no regressions)

---

## Acceptance Tests

| ID | Scenario | Given | When | Then |
|----|----------|-------|------|------|
| AT-001 | Flink fraud detection | Generator sends 100 transactions to Kafka | Flink processes events | Bronze table has 100 rows, fraud alerts emitted for score > 0.7 |
| AT-002 | dbt staging transform | Bronze has raw transactions | `dbt run --select staging` | Silver.clean_transactions populated with correct types and quality_checks |
| AT-003 | dbt marts transform | Silver has clean data | `dbt run --select marts` | Gold dimensions and facts populated, aggregates computed |
| AT-004 | dbt quality checks | Silver has data with known null rates | `dbt test` | All schema tests pass (not_null, unique, accepted_values) |
| AT-005 | Cosmos DAG visibility | Airflow has dbt_staging DAG | User opens Airflow UI | Sees individual dbt model tasks (stg_transactions, stg_fraud_alerts, etc.) |
| AT-006 | End-to-end pipeline | Fresh K3s cluster | `./scripts/demo.sh` | Data flows from generator through Gold layer in <15 minutes |
| AT-007 | Schema mismatch fix | Old SQL had column mismatches | dbt models run | All models succeed with correct column names matching DDL |
| AT-008 | No regression | All existing tests | `pytest tests/` | 263+ tests pass |

---

## Out of Scope

- Grafana dashboards (RAM constraint on K3s)
- Prometheus active scraping (no Prometheus pod)
- dbt Cloud integration ($0 budget)
- elementary data observability (overkill for portfolio)
- Multi-environment dbt profiles (single K3s node)
- Helm chart packaging (raw manifests + Kustomize sufficient)
- HA / multi-node K3s
- TLS/HTTPS ingress

---

## Constraints

| Type | Constraint | Impact |
|------|------------|--------|
| Infrastructure | K3s: 4 cores, ~5.7GB free RAM, 527GB disk | Single-replica everything, no Prometheus/Grafana |
| Budget | $0 — all open-source | No cloud services, no paid registries |
| Registry | Local K3s (k3s ctr images import) | No ghcr.io, images built locally or imported |
| Compatibility | Python 3.11+ | dbt-core 1.9+ requires 3.9+, safe |
| Flink | PyFlink (no Java) | Custom Docker image, no JAR build |
| Network | Single-node K3s | All services on same node, inter-namespace networking |

---

## Technical Context

| Aspect | Value | Notes |
|--------|-------|-------|
| **Deployment Location** | `dbt/`, `docker/`, `src/dags/`, `scripts/`, `k8s/`, `.github/workflows/` | New dbt project + Dockerfiles + updated DAGs |
| **KB Domains** | dbt, cosmos, docker, k3s, airflow, flink | New KB domains needed for dbt patterns |
| **IaC Impact** | Modify existing Terraform (Airflow Helm values) + new Docker build scripts | Airflow values need cosmos + dbt deps |

---

## Assumptions

| ID | Assumption | If Wrong, Impact | Validated? |
|----|------------|------------------|------------|
| A-001 | K3s server is accessible and K3s is running | Cannot deploy anything | [x] Verified via SSH |
| A-002 | 5.7GB RAM is enough for Kafka + Flink + PG + Airflow (minimal) | OOM kills, need swap or reduce components | [ ] Need to test |
| A-003 | PyFlink Python app mode works without JAR on Flink K8s Operator | May need minimal JAR shim | [ ] Need to test |
| A-004 | Astronomer Cosmos works with Airflow 2.x on K8s | Compatibility issue | [ ] Check docs |
| A-005 | dbt-postgres adapter connects to CloudNativePG | Standard PostgreSQL protocol | [x] CNPG is Postgres-compatible |
| A-006 | Existing Bronze schema DDL is correct | dbt sources won't match | [x] Verified in migrations |

---

## Deliverables by Phase

### Phase 1: Containerization Foundation
| # | Deliverable | Type | Location |
|---|------------|------|----------|
| 1.1 | Flink Dockerfile (PyFlink + scikit-learn + source) | Docker | `docker/flink/Dockerfile` |
| 1.2 | Generator Dockerfile (confluent-kafka + generators) | Docker | `docker/generator/Dockerfile` |
| 1.3 | Airflow Dockerfile (dbt + cosmos + dbt-postgres) | Docker | `docker/airflow/Dockerfile` |
| 1.4 | Image build script | Script | `scripts/build_images.sh` |
| 1.5 | K3s image import script | Script | `scripts/import_images.sh` |
| 1.6 | Updated Flink manifests (PyFlink app mode) | K8s | `k8s/flink/*.yaml` |
| 1.7 | CI Docker build job | CI | `.github/workflows/ci.yaml` |

### Phase 2: dbt Project
| # | Deliverable | Type | Location |
|---|------------|------|----------|
| 2.1 | dbt project config | Config | `dbt/dbt_project.yml` |
| 2.2 | dbt profiles | Config | `dbt/profiles.yml` |
| 2.3 | dbt packages | Config | `dbt/packages.yml` |
| 2.4 | Staging models (Bronze→Silver) | SQL | `dbt/models/staging/` |
| 2.5 | Staging sources + schema | YAML | `dbt/models/staging/_staging__sources.yml` |
| 2.6 | Intermediate models | SQL | `dbt/models/intermediate/` |
| 2.7 | Marts models (Silver→Gold) | SQL | `dbt/models/marts/` |
| 2.8 | Marts schema tests | YAML | `dbt/models/marts/_marts__schema.yml` |
| 2.9 | Singular tests (quality checks) | SQL | `dbt/tests/` |
| 2.10 | Custom macros | SQL | `dbt/macros/` |

### Phase 3: Airflow + Cosmos DAGs
| # | Deliverable | Type | Location |
|---|------------|------|----------|
| 3.1 | dbt_staging DAG (Cosmos) | Python | `src/dags/dbt_staging.py` |
| 3.2 | dbt_marts DAG (Cosmos) | Python | `src/dags/dbt_marts.py` |
| 3.3 | dbt_quality DAG (Cosmos) | Python | `src/dags/dbt_quality.py` |
| 3.4 | Airflow Helm values update | Terraform | `infra/modules/airflow/` |
| 3.5 | Remove old DAGs | Python | Delete `bronze_to_silver.py`, `silver_to_gold.py`, `data_quality.py` |
| 3.6 | DAG import tests | Python | `tests/unit/test_dbt_dags.py` |

### Phase 4: End-to-End Integration
| # | Deliverable | Type | Location |
|---|------------|------|----------|
| 4.1 | Updated deploy.sh v2 | Script | `scripts/deploy.sh` |
| 4.2 | K3s setup script | Script | `scripts/setup_k3s.sh` |
| 4.3 | Demo script (one-command) | Script | `scripts/demo.sh` |
| 4.4 | Generator as K8s Deployment | K8s | `k8s/generator/deployment.yaml` |
| 4.5 | ML model in Flink image | Docker | Built into `docker/flink/Dockerfile` |
| 4.6 | Airflow connection provisioning | Terraform | `infra/modules/airflow/` |

### Phase 5: Staff Polish
| # | Deliverable | Type | Location |
|---|------------|------|----------|
| 5.1 | Updated README with dbt architecture | Docs | `README.md` |
| 5.2 | ADR-013: dbt over raw SQL | ADR | `docs/adr/013-dbt-over-raw-sql.md` |
| 5.3 | ADR-014: Cosmos Airflow integration | ADR | `docs/adr/014-cosmos-airflow-integration.md` |
| 5.4 | ADR-015: PyFlink Docker (no JAR) | ADR | `docs/adr/015-pyflink-docker-no-jar.md` |
| 5.5 | Updated SETUP_GUIDE | Docs | `docs/SETUP_GUIDE.md` |
| 5.6 | All CI checks green | CI | `.github/workflows/ci.yaml` |

---

## Known SQL Bugs to Fix in dbt Migration

| Bug | Location | Fix in dbt |
|-----|----------|------------|
| `silver.fraud_alerts` referenced but never created | `load_fact_fraud_alerts.sql` | dbt model will join from `bronze.raw_fraud_alerts` directly |
| Column `email` in `upsert_dim_customer.sql` not in schema | Gold transforms | dbt model will use correct columns from `silver.customers` |
| `latitude/longitude` in `upsert_dim_store.sql` not in `gold.dim_store` | Gold transforms | dbt model will match DDL |
| `hour_bucket` vs `hour_timestamp` mismatch | `refresh_hourly_sales.sql` | dbt model will use correct column names |
| `day_bucket` vs `date_key` mismatch | `refresh_daily_fraud.sql` | dbt model will use correct column names |
| `refreshed_at` not in aggregate schemas | All aggregate transforms | dbt handles `updated_at` via config |

---

## Clarity Score Breakdown

| Element | Score (0-3) | Notes |
|---------|-------------|-------|
| Problem | 3 | Crystal clear: code doesn't deploy, needs dbt + Docker + E2E |
| Users | 3 | Well-defined: hiring manager, interviewer, author |
| Goals | 3 | MoSCoW prioritized with clear MUST/SHOULD/COULD |
| Success | 3 | All measurable with concrete numbers |
| Scope | 2 | Clear scope, minor uncertainty on PyFlink app mode compatibility |
| **Total** | **14/15** | |

---

## Open Questions

1. **PyFlink app mode on Flink K8s Operator:** Does it work without a JAR at all, or does it need a minimal PyFlink runner JAR? Need to verify during Phase 1.
2. **Cosmos + Airflow version compatibility:** Confirm cosmos works with the Airflow version in our Helm chart.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-18 | define-agent | Initial version from brainstorm |

---

## Next Step

**Ready for:** `/design .claude/sdd/features/DEFINE_E2E_PRODUCTION.md`
