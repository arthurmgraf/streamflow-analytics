# StreamFlow Analytics - Setup Guide

## Overview

This guide provides step-by-step instructions for deploying the StreamFlow Analytics platform on a K3s single-node cluster. The platform is a real-time streaming data system for e-commerce fraud detection, built on Kubernetes-native components.

**Target Environment:** Single-node K3s cluster (<YOUR_SERVER_IP>)
**Stack:** Strimzi Kafka, Flink, CloudNativePG, Airflow, Prometheus/Grafana
**Architecture:** 5 Kubernetes namespaces with Medallion data architecture

---

## Prerequisites

### Required Software

Before starting the deployment, ensure the following tools are installed:

| Tool | Version | Purpose |
|------|---------|---------|
| **K3s** | v1.34+ | Lightweight Kubernetes distribution |
| **kubectl** | Compatible with K3s | Kubernetes CLI |
| **Terraform** | 1.7+ | Infrastructure provisioning |
| **Terragrunt** | Latest | Terraform orchestration |
| **Python** | 3.11+ | Data generation and migration scripts |
| **Helm** | 3.0+ | Kubernetes package manager |
| **Git** | Any | Version control |

### System Requirements

- **Server:** <YOUR_SERVER_IP>
- **CPU:** 4 cores
- **Memory:** 9.7 GB RAM
- **Disk:** 598 GB available
- **OS:** Ubuntu 22.04 LTS
- **Network:** Public IP with SSH access

### Verify K3s Installation

```bash
# Check K3s is running
kubectl get nodes

# Expected output:
# NAME     STATUS   ROLES                  AGE   VERSION
# server   Ready    control-plane,master   Xd    v1.34.x
```

### Install Python Dependencies

```bash
# From project root
pip install -r requirements.txt

# Required packages:
# - psycopg2-binary (PostgreSQL driver)
# - pyyaml (Configuration parsing)
# - kafka-python (Event generation)
# - faker (Test data generation)
```

---

## Step 1: Clone and Configure

### Clone Repository

```bash
git clone <repository-url>
cd streamflow-analytics
```

### Configure Environment Variables

Create a `.env.local` file in the project root:

```bash
# .env.local
POSTGRES_PASSWORD=<strong-password-here>
SERVER_IP=<YOUR_SERVER_IP>
ENVIRONMENT=dev

# Optional: Custom configurations
KAFKA_REPLICAS=1
FLINK_TASKMANAGERS=2
AIRFLOW_WORKERS=1
```

**Security Note:** Never commit `.env.local` to version control. It's included in `.gitignore`.

### Generate Secrets

```bash
# Generate strong passwords for services
python scripts/generate_secrets.py

# This creates:
# - infra/secrets/postgres.yaml
# - infra/secrets/airflow.yaml
# - infra/secrets/flink.yaml
```

---

## Step 2: Deploy Infrastructure

The infrastructure deployment follows a 6-module dependency chain managed by Terragrunt:

```text
┌─────────────────┐
│   namespaces    │  (1) Create 5 K8s namespaces
└────────┬────────┘
         │
    ┌────┴─────┬──────────┬────────────┐
    │          │          │            │
┌───▼───┐  ┌──▼───┐  ┌───▼────┐  ┌────▼─────┐
│ kafka │  │ flink│  │postgres│  │monitoring│  (2-5) Core services
└───┬───┘  └──┬───┘  └───┬────┘  └──────────┘
    │         │          │
    └────┬────┴──────────┘
         │
    ┌────▼────┐
    │ airflow │  (6) Orchestration (depends on all)
    └─────────┘
```

### Module Descriptions

| Module | Namespace | Purpose | Dependencies |
|--------|-----------|---------|--------------|
| **namespaces** | All 5 | Creates namespace structure | None |
| **kafka** | streamflow-kafka | Strimzi Kafka (KRaft mode) | namespaces |
| **flink** | streamflow-processing | Flink K8s Operator | namespaces |
| **postgresql** | streamflow-data | CloudNativePG cluster | namespaces |
| **monitoring** | streamflow-monitoring | kube-prometheus-stack | namespaces |
| **airflow** | streamflow-orchestration | Airflow LocalExecutor | kafka, flink, postgresql |

### Deploy All Modules

```bash
# From infra/ directory
cd infra

# Preview deployment plan
terragrunt run-all plan

# Deploy infrastructure (10-15 minutes)
terragrunt run-all apply --terragrunt-non-interactive

# Monitor deployment
watch kubectl get pods -A
```

### Verify Deployment

```bash
# Check all StreamFlow pods are running
kubectl get pods -A | grep streamflow

# Expected namespaces and pod counts:
# streamflow-kafka          : 3-5 pods (Kafka cluster, ZooKeeper)
# streamflow-processing     : 2-4 pods (Flink JobManager, TaskManagers)
# streamflow-data          : 3 pods (PostgreSQL primary, replicas)
# streamflow-orchestration : 3-5 pods (Airflow scheduler, webserver, workers)
# streamflow-monitoring    : 10+ pods (Prometheus, Grafana, exporters)
```

### Troubleshooting Deployment

**Issue: Pods stuck in Pending state**

```bash
# Check resource constraints
kubectl describe pod <pod-name> -n <namespace>

# Common causes:
# - Insufficient memory (reduce replica counts in terragrunt.hcl)
# - PVC binding issues (check storage class)
# - Image pull errors (check imagePullPolicy)
```

**Issue: Kafka broker not starting**

```bash
# Check Kafka logs
kubectl logs -n streamflow-kafka <kafka-pod> -f

# Verify KRaft configuration
kubectl get kafka -n streamflow-kafka -o yaml

# Common fix: Restart Strimzi operator
kubectl rollout restart deployment strimzi-cluster-operator -n streamflow-kafka
```

**Issue: PostgreSQL cluster not forming**

```bash
# Check CloudNativePG operator
kubectl get cluster -n streamflow-data

# View cluster status
kubectl cnpg status streamflow-postgres -n streamflow-data

# Check PVC creation
kubectl get pvc -n streamflow-data
```

---

## Step 3: Run Database Migrations

After PostgreSQL is running, initialize the Medallion architecture:

```bash
# From project root
python scripts/run_migrations.py --env dev

# Migration process:
# 1. Creates schemas: bronze, silver, gold
# 2. Creates tables in each layer
# 3. Sets up foreign keys and indexes
# 4. Creates materialized views for gold layer
# 5. Grants permissions to application roles
```

### Migration Files

Migrations are located in `infra/postgresql/migrations/`:

```text
migrations/
├── V001__create_schemas.sql         # Bronze, Silver, Gold schemas
├── V002__bronze_tables.sql          # Raw event tables
├── V003__silver_tables.sql          # Cleaned, enriched tables
├── V004__gold_tables.sql            # Aggregated analytics tables
├── V005__fraud_detection.sql        # Fraud rules and alerts
├── V006__indexes.sql                # Performance indexes
└── V007__materialized_views.sql     # Precomputed views
```

### Verify Migrations

```bash
# Connect to PostgreSQL
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres

# Check schemas
\dn

# Expected output:
#   Name   | Owner
# ---------+----------
#  bronze  | postgres
#  silver  | postgres
#  gold    | postgres

# Check tables in each schema
\dt bronze.*
\dt silver.*
\dt gold.*

# Exit
\q
```

---

## Step 4: Seed Reference Data

Populate lookup tables and reference data:

```bash
# Seed reference data
python scripts/seed_data.py

# This populates:
# - bronze.stores (100 store locations)
# - bronze.customers (10,000 customers)
# - bronze.payment_methods (credit_card, debit_card, paypal, etc.)
# - silver.fraud_rules (5 detection rules FR-001 to FR-005)
# - silver.blacklist (test blacklisted entities)
```

### Verify Seed Data

```bash
# Check record counts
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres -c "
SELECT
  'bronze.stores' as table_name, COUNT(*) as count FROM bronze.stores
  UNION ALL
SELECT 'bronze.customers', COUNT(*) FROM bronze.customers
  UNION ALL
SELECT 'bronze.payment_methods', COUNT(*) FROM bronze.payment_methods
  UNION ALL
SELECT 'silver.fraud_rules', COUNT(*) FROM silver.fraud_rules
  UNION ALL
SELECT 'silver.blacklist', COUNT(*) FROM silver.blacklist;
"
```

---

## Step 5: Verify All Services

### Check Pod Status

```bash
# All StreamFlow pods should be Running
kubectl get pods -A | grep streamflow

# Check for any CrashLoopBackOff or Error states
kubectl get pods -A | grep -E 'CrashLoop|Error|Pending'
```

### Verify Kafka Topics

```bash
# List topics
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Expected topics:
# - transactions.raw
# - transactions.enriched
# - fraud.alerts
# - fraud.scored
```

### Verify Flink Jobs

```bash
# Check Flink JobManager
kubectl get pods -n streamflow-processing

# Port-forward to Flink UI (see Step 7)
```

### Verify PostgreSQL

```bash
# Test connection
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "SELECT version();"

# Check database size
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  schemaname,
  pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))::bigint) as size
FROM pg_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
GROUP BY schemaname;
"
```

---

## Step 6: Access Service UIs

### Grafana (Monitoring Dashboards)

```bash
# Port-forward Grafana
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-grafana 3000:80

# Access: http://localhost:3000
# Default credentials:
#   Username: admin
#   Password: prom-operator
```

**Available Dashboards:**
- Kafka Cluster Overview
- Flink Jobs Monitoring
- PostgreSQL Performance
- Fraud Detection Metrics
- Pipeline Latency

### Airflow (Orchestration)

```bash
# Port-forward Airflow webserver
kubectl port-forward -n streamflow-orchestration svc/airflow-webserver 8080:8080

# Access: http://localhost:8080
# Default credentials:
#   Username: admin
#   Password: <from secrets>
```

**Available DAGs:**
- `bronze_to_silver_pipeline` - Data cleaning and enrichment
- `silver_to_gold_pipeline` - Aggregation and analytics
- `fraud_detection_batch` - Batch fraud scoring
- `maintenance_tasks` - Daily maintenance (03:00 UTC)

### Flink Web UI

```bash
# Port-forward Flink JobManager
kubectl port-forward -n streamflow-processing svc/flink-jobmanager 8081:8081

# Access: http://localhost:8081
```

**Features:**
- Running Jobs status
- TaskManager metrics
- Job configuration
- Checkpoint statistics
- Backpressure monitoring

---

## Step 7: Start Event Generation

Generate synthetic e-commerce transactions:

```bash
# Generate events at 100 transactions/second for 10 minutes
python scripts/generate_events.py --rate 100 --duration 600

# Options:
#   --rate: Events per second (default: 100)
#   --duration: Runtime in seconds (default: 300)
#   --fraud-rate: Percentage of fraudulent transactions (default: 0.05)
#   --kafka-broker: Kafka bootstrap server (default: localhost:9092)
```

### Event Generation Features

- Realistic customer behavior patterns
- Geographic distribution across stores
- Time-based shopping patterns (peak hours: 12-14, 18-20)
- Fraud injection based on configured rate
- Configurable transaction value distribution

### Port-Forward Kafka for Local Access

```bash
# Expose Kafka broker
kubectl port-forward -n streamflow-kafka svc/streamflow-kafka-kafka-bootstrap 9092:9092

# Now generate_events.py can connect to localhost:9092
```

---

## Step 8: Verify Pipeline Data Flow

### Check Bronze Layer (Raw Events)

```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres -c "
SELECT
  COUNT(*) as total_transactions,
  MIN(transaction_time) as earliest,
  MAX(transaction_time) as latest
FROM bronze.transactions;
"
```

### Check Silver Layer (Enriched Events)

```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres -c "
SELECT
  COUNT(*) as total_enriched,
  COUNT(DISTINCT customer_id) as unique_customers,
  COUNT(DISTINCT store_id) as unique_stores
FROM silver.transactions_enriched;
"
```

### Check Gold Layer (Aggregations)

```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres -c "
SELECT
  date_trunc('hour', hour) as hour,
  total_transactions,
  total_amount,
  avg_amount
FROM gold.hourly_metrics
ORDER BY hour DESC
LIMIT 24;
"
```

### Check Fraud Alerts

```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres -c "
SELECT
  rule_id,
  COUNT(*) as alert_count,
  AVG(fraud_score) as avg_score
FROM silver.fraud_alerts
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY rule_id
ORDER BY alert_count DESC;
"
```

---

## Step 9: Monitor Pipeline Health

### View Real-Time Metrics in Grafana

1. Open Grafana (http://localhost:3000)
2. Navigate to "StreamFlow Analytics" dashboard
3. Verify metrics:
   - Kafka consumer lag < 1000 messages
   - Flink job state: RUNNING
   - PostgreSQL connections < 80% max
   - Fraud detection latency < 500ms

### Check Airflow DAG Runs

1. Open Airflow UI (http://localhost:8080)
2. Verify DAGs are enabled and running:
   - `bronze_to_silver_pipeline`: Every 5 minutes
   - `silver_to_gold_pipeline`: Every 15 minutes
   - `fraud_detection_batch`: Every hour
3. Check for failed tasks (red squares)

### Monitor Kafka Consumer Lag

```bash
# Check consumer group lag
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group flink-fraud-detector

# Expected lag: < 1000 messages
```

### Check Flink Job Status

```bash
# List running jobs
kubectl exec -it deployment/flink-jobmanager -n streamflow-processing -- \
  bin/flink list

# Expected output:
# - FraudDetectionJob [RUNNING]
# - TransactionEnrichmentJob [RUNNING]
```

---

## Step 10: Troubleshooting

### Common Issues and Solutions

#### Issue: Kafka Consumer Lag Increasing

**Symptoms:** Consumer lag > 10,000 messages and growing

**Diagnosis:**
```bash
# Check Flink TaskManager resources
kubectl top pods -n streamflow-processing

# View Flink backpressure
# Access Flink UI → Running Jobs → Click job → Backpressure tab
```

**Solutions:**
1. Increase Flink parallelism in `infra/flink/terragrunt.hcl`:
   ```hcl
   task_managers = 3  # Increase from 2
   task_slots = 2     # Total parallelism = 6
   ```
2. Scale up TaskManager memory:
   ```hcl
   taskmanager_memory = "2Gi"  # Increase from 1Gi
   ```
3. Re-apply Terraform:
   ```bash
   cd infra/flink
   terragrunt apply
   ```

#### Issue: PostgreSQL Connection Pool Exhausted

**Symptoms:** Airflow tasks failing with "too many connections"

**Diagnosis:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres -c "
SELECT COUNT(*), state
FROM pg_stat_activity
GROUP BY state;
"
```

**Solutions:**
1. Increase PostgreSQL max_connections:
   ```bash
   # Edit CloudNativePG cluster
   kubectl edit cluster streamflow-postgres -n streamflow-data

   # Add under postgresql.parameters:
   max_connections: "200"  # Increase from 100
   ```
2. Reduce Airflow connection pool:
   ```bash
   # Edit Airflow ConfigMap
   kubectl edit configmap airflow-config -n streamflow-orchestration

   # Set: sql_alchemy_pool_size: 10
   ```

#### Issue: Flink Job in RESTARTING State

**Symptoms:** Flink job constantly restarting, no progress

**Diagnosis:**
```bash
# View Flink logs
kubectl logs -n streamflow-processing deployment/flink-jobmanager -f

# Common errors:
# - "OutOfMemoryError: Java heap space"
# - "Checkpoint timeout"
# - "Kafka broker connection failed"
```

**Solutions:**

**For Memory Issues:**
```hcl
# In infra/flink/terragrunt.hcl
jobmanager_memory = "2Gi"  # Increase from 1Gi
```

**For Checkpoint Issues:**
```python
# In src/flink_jobs/fraud_detector.py
env.get_checkpoint_config().set_checkpoint_timeout(600000)  # 10 minutes
```

**For Kafka Connection Issues:**
```bash
# Verify Kafka is reachable from Flink namespace
kubectl run -it --rm debug -n streamflow-processing --image=busybox -- \
  nc -zv streamflow-kafka-kafka-bootstrap.streamflow-kafka.svc.cluster.local 9092
```

#### Issue: Airflow Scheduler Not Picking Up DAGs

**Symptoms:** DAGs not appearing in Airflow UI

**Diagnosis:**
```bash
# Check scheduler logs
kubectl logs -n streamflow-orchestration deployment/airflow-scheduler -f

# Verify DAGs directory mounted
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  ls -la /opt/airflow/dags
```

**Solutions:**
1. Restart Airflow scheduler:
   ```bash
   kubectl rollout restart deployment/airflow-scheduler -n streamflow-orchestration
   ```
2. Verify DAG syntax:
   ```bash
   python src/airflow_dags/bronze_to_silver.py
   # Should run without errors
   ```

#### Issue: Grafana Dashboards Showing No Data

**Symptoms:** All Grafana panels show "No Data"

**Diagnosis:**
```bash
# Check Prometheus targets
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-prometheus 9090:9090

# Access: http://localhost:9090/targets
# Verify all targets are "UP"
```

**Solutions:**
1. Verify ServiceMonitor resources:
   ```bash
   kubectl get servicemonitor -A
   ```
2. Check Prometheus scrape config:
   ```bash
   kubectl get secret -n streamflow-monitoring kube-prometheus-stack-prometheus -o yaml
   ```
3. Restart Prometheus:
   ```bash
   kubectl rollout restart statefulset/prometheus-kube-prometheus-stack-prometheus -n streamflow-monitoring
   ```

---

## Next Steps

After successful deployment:

1. **Review Fraud Detection Rules:** See [FRAUD_DETECTION.md](FRAUD_DETECTION.md)
2. **Configure Alerting:** Set up Slack/email notifications in Alertmanager
3. **Tune Performance:** Adjust resource limits based on actual load
4. **Set Up Backups:** Configure CloudNativePG backup schedule
5. **Review Operations:** See [RUNBOOK.md](RUNBOOK.md) for operational procedures

---

## Deployment Checklist

- [ ] All prerequisites installed (K3s, kubectl, Terraform, Python)
- [ ] `.env.local` configured with strong passwords
- [ ] `terragrunt run-all apply` completed successfully
- [ ] All pods in Running state (no CrashLoopBackOff)
- [ ] Database migrations applied successfully
- [ ] Reference data seeded
- [ ] Kafka topics created and accessible
- [ ] Flink jobs submitted and running
- [ ] Airflow DAGs enabled and scheduling
- [ ] Grafana dashboards showing data
- [ ] Event generator producing transactions
- [ ] Bronze → Silver → Gold data flow verified
- [ ] Fraud alerts being generated

---

## Support and Documentation

- **Operational Procedures:** [RUNBOOK.md](RUNBOOK.md)
- **Fraud Detection Details:** [FRAUD_DETECTION.md](FRAUD_DETECTION.md)
- **Architecture Diagrams:** [design/architecture.md](../design/architecture.md)
- **API Documentation:** [design/api-spec.md](../design/api-spec.md)

For issues not covered in this guide, check the project's issue tracker or contact the platform team.
