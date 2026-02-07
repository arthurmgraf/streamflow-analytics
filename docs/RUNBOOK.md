# StreamFlow Analytics - Operations Runbook

## Overview

This runbook provides operational procedures for monitoring, maintaining, and troubleshooting the StreamFlow Analytics platform in production. It is designed for DevOps engineers, SREs, and on-call personnel.

**Platform:** K3s single-node cluster (<YOUR_SERVER_IP>)
**Monitoring:** kube-prometheus-stack (Prometheus + Grafana + Alertmanager)
**Alert Channels:** Slack #streamflow-alerts, PagerDuty (critical only)

---

## Quick Reference

### Critical Commands

```bash
# Health check all StreamFlow services
kubectl get pods -A | grep streamflow

# View recent alerts
kubectl get prometheusrules -A | grep streamflow

# Restart a crashed service
kubectl rollout restart deployment/<name> -n <namespace>

# Check resource usage
kubectl top pods -A | grep streamflow

# View logs for a service
kubectl logs -n <namespace> <pod-name> -f --tail=100
```

### Emergency Contacts

| Severity | Contact | Response Time |
|----------|---------|---------------|
| **Critical** (P1) | PagerDuty: +1-XXX-XXX-XXXX | < 15 minutes |
| **High** (P2) | Slack: @oncall-engineer | < 1 hour |
| **Medium** (P3) | Slack: #streamflow-support | < 4 hours |
| **Low** (P4) | Jira ticket | Next business day |

---

## Service Health Checks

### 1. Kafka Cluster (streamflow-kafka namespace)

**Check Kafka broker status:**
```bash
kubectl get kafka -n streamflow-kafka

# Expected output:
# NAME               DESIRED REPLICAS   READY
# streamflow-kafka   1                  True
```

**Check Kafka pods:**
```bash
kubectl get pods -n streamflow-kafka

# Expected pods:
# - streamflow-kafka-kafka-0 (Running)
# - streamflow-kafka-entity-operator-* (Running)
# - strimzi-cluster-operator-* (Running)
```

**Verify Kafka topics:**
```bash
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Expected topics:
# transactions.raw
# transactions.enriched
# fraud.alerts
# fraud.scored
# fraud.blacklist
```

**Check topic health:**
```bash
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic transactions.raw

# Verify:
# - Partition count: 3
# - Replication factor: 1 (single-node)
# - Leader: 0 (broker ID)
# - ISR: 0 (in-sync replicas)
```

**Health Indicators:**
- ✅ All pods in Running state
- ✅ Kafka cluster Ready: True
- ✅ All topics have leader assigned
- ✅ ISR matches replication factor

**Unhealthy Signals:**
- ❌ Pod in CrashLoopBackOff
- ❌ Kafka cluster Ready: False
- ❌ Topics have no leader
- ❌ Under-replicated partitions (ISR < replication factor)

---

### 2. Flink Cluster (streamflow-processing namespace)

**Check Flink deployments:**
```bash
kubectl get deployments -n streamflow-processing

# Expected deployments:
# flink-kubernetes-operator (1/1 ready)
# flink-jobmanager (1/1 ready)
```

**Check Flink pods:**
```bash
kubectl get pods -n streamflow-processing

# Expected pods:
# - flink-kubernetes-operator-* (Running)
# - flink-jobmanager-* (Running)
# - flink-taskmanager-* (2 replicas, Running)
```

**Check Flink job status:**
```bash
# Port-forward to Flink REST API
kubectl port-forward -n streamflow-processing svc/flink-jobmanager-rest 8081:8081 &

# List jobs
curl -s http://localhost:8081/jobs | jq '.jobs'

# Expected output:
# [
#   {
#     "id": "<job-id>",
#     "status": "RUNNING"
#   }
# ]
```

**Check job details:**
```bash
# Get job ID
JOB_ID=$(curl -s http://localhost:8081/jobs | jq -r '.jobs[0].id')

# Get job status
curl -s http://localhost:8081/jobs/$JOB_ID | jq '.state'

# Expected: "RUNNING"
```

**Check checkpoint status:**
```bash
curl -s http://localhost:8081/jobs/$JOB_ID/checkpoints | jq '{
  latest: .latest.completed.id,
  duration: .latest.completed.duration,
  state_size: .latest.completed.state_size
}'
```

**Health Indicators:**
- ✅ JobManager and TaskManagers running
- ✅ Job state: RUNNING
- ✅ Checkpoints completing successfully
- ✅ No backpressure (check Flink UI)

**Unhealthy Signals:**
- ❌ Job state: RESTARTING, FAILED, or CANCELED
- ❌ Checkpoints failing (no successful checkpoint in 10+ minutes)
- ❌ High backpressure (>80% on operators)
- ❌ TaskManager out of memory errors

---

### 3. PostgreSQL Cluster (streamflow-data namespace)

**Check CloudNativePG cluster:**
```bash
kubectl get cluster -n streamflow-data

# Expected output:
# NAME                 AGE   INSTANCES   READY   STATUS
# streamflow-postgres  Xd    3           3       Cluster in healthy state
```

**Check PostgreSQL pods:**
```bash
kubectl get pods -n streamflow-data

# Expected pods:
# - streamflow-postgres-1 (primary, Running)
# - streamflow-postgres-2 (replica, Running)
# - streamflow-postgres-3 (replica, Running)
```

**Identify primary instance:**
```bash
kubectl get cluster streamflow-postgres -n streamflow-data -o jsonpath='{.status.currentPrimary}'

# Expected: streamflow-postgres-1
```

**Check database connection:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "SELECT version();"
```

**Check active connections:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  count(*) as total_connections,
  max_conn,
  ROUND(100.0 * count(*) / max_conn, 2) as pct_used
FROM pg_stat_activity, (SELECT setting::int AS max_conn FROM pg_settings WHERE name='max_connections') mc
GROUP BY max_conn;
"

# Healthy: < 80% connections used
```

**Check table sizes:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
  n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

**Check replication lag (if replicas configured):**
```bash
# On primary
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  application_name,
  client_addr,
  state,
  sync_state,
  pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes
FROM pg_stat_replication;
"

# Healthy: lag_bytes < 10 MB
```

**Check database vacuum status:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  schemaname,
  relname,
  last_vacuum,
  last_autovacuum,
  n_dead_tup
FROM pg_stat_user_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
ORDER BY n_dead_tup DESC
LIMIT 10;
"

# Warning: n_dead_tup > 100,000 (may need manual VACUUM)
```

**Health Indicators:**
- ✅ Cluster status: "Cluster in healthy state"
- ✅ All pods running (1 primary + N replicas)
- ✅ Connection usage < 80%
- ✅ Replication lag < 10 MB
- ✅ Recent vacuum activity

**Unhealthy Signals:**
- ❌ Cluster status: "Cluster in degraded state"
- ❌ Primary pod not running
- ❌ Connection pool exhausted (100% connections)
- ❌ Replication lag > 100 MB
- ❌ High dead tuple count (> 100,000)

---

### 4. Airflow (streamflow-orchestration namespace)

**Check Airflow deployments:**
```bash
kubectl get deployments -n streamflow-orchestration

# Expected deployments:
# airflow-scheduler (1/1 ready)
# airflow-webserver (1/1 ready)
# airflow-worker (1/1 ready - if CeleryExecutor)
```

**Check Airflow pods:**
```bash
kubectl get pods -n streamflow-orchestration

# Expected pods:
# - airflow-scheduler-* (Running)
# - airflow-webserver-* (Running)
# - airflow-worker-* (Running, if CeleryExecutor)
# - airflow-postgresql-* (Running)
```

**Port-forward to Airflow UI:**
```bash
kubectl port-forward -n streamflow-orchestration svc/airflow-webserver 8080:8080

# Access: http://localhost:8080
```

**Check DAG status via CLI:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list

# Expected DAGs:
# bronze_to_silver_pipeline
# silver_to_gold_pipeline
# fraud_detection_batch
# maintenance_tasks
```

**Check DAG run status:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --state failed --dag-id bronze_to_silver_pipeline

# Healthy: No failed runs in last 24 hours
```

**Check scheduler heartbeat:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow jobs check --job-type SchedulerJob --limit 1

# Expected: Recent heartbeat (< 1 minute ago)
```

**Health Indicators:**
- ✅ Scheduler heartbeat recent (< 1 minute)
- ✅ Webserver responding on port 8080
- ✅ DAGs enabled and scheduled
- ✅ No failed DAG runs in last 24 hours

**Unhealthy Signals:**
- ❌ Scheduler heartbeat stale (> 5 minutes)
- ❌ Webserver returning 500 errors
- ❌ DAGs paused or deleted
- ❌ Multiple consecutive DAG failures

---

### 5. Monitoring Stack (streamflow-monitoring namespace)

**Check Prometheus:**
```bash
kubectl get pods -n streamflow-monitoring | grep prometheus

# Expected:
# prometheus-kube-prometheus-stack-prometheus-0 (Running)
```

**Check Prometheus targets:**
```bash
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-prometheus 9090:9090

# Access: http://localhost:9090/targets
# Verify all targets are "UP"
```

**Check Grafana:**
```bash
kubectl get pods -n streamflow-monitoring | grep grafana

# Expected:
# kube-prometheus-stack-grafana-* (Running)
```

**Check Alertmanager:**
```bash
kubectl get pods -n streamflow-monitoring | grep alertmanager

# Expected:
# alertmanager-kube-prometheus-stack-alertmanager-0 (Running)
```

**View active alerts:**
```bash
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-alertmanager 9093:9093

# Access: http://localhost:9093/#/alerts
```

**Health Indicators:**
- ✅ Prometheus scraping all targets
- ✅ Grafana dashboards loading
- ✅ Alertmanager routing notifications
- ✅ No critical alerts firing

---

## Kafka Operations

### Check Consumer Lag

**Via Kafka CLI:**
```bash
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --all-groups

# Key columns:
# - CURRENT-OFFSET: Latest offset consumed
# - LOG-END-OFFSET: Latest offset produced
# - LAG: Messages behind
```

**Via Prometheus query:**
```promql
kafka_consumergroup_lag{group="flink-fraud-detector"}
```

**Healthy lag:** < 1,000 messages (< 10 seconds at 100 msg/s)
**Warning:** 1,000 - 10,000 messages (10-100 seconds)
**Critical:** > 10,000 messages (> 100 seconds)

### Restart Kafka Broker

**Single broker (single-node cluster):**
```bash
# Delete pod (StatefulSet will recreate)
kubectl delete pod streamflow-kafka-kafka-0 -n streamflow-kafka

# Wait for pod to be ready
kubectl wait --for=condition=ready pod/streamflow-kafka-kafka-0 -n streamflow-kafka --timeout=300s

# Verify broker is up
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

**Impact:** 30-60 seconds downtime, producer retries will buffer messages

### Increase Kafka Retention

**Temporary increase (via CLI):**
```bash
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-configs.sh --bootstrap-server localhost:9092 \
  --entity-type topics --entity-name transactions.raw \
  --alter --add-config retention.ms=604800000

# 604800000 ms = 7 days
```

**Permanent increase (via Terraform):**
```hcl
# In infra/kafka/main.tf
resource "kafka_topic" "transactions_raw" {
  name               = "transactions.raw"
  partitions         = 3
  replication_factor = 1
  config = {
    "retention.ms" = "604800000"  # 7 days
  }
}
```

### Rebalance Consumer Groups

**Trigger rebalance (restart Flink job):**
```bash
# Delete Flink job pod
kubectl delete pod -n streamflow-processing -l app=flink,component=jobmanager

# Flink will restart and trigger consumer group rebalance
```

**Monitor rebalance:**
```bash
kubectl logs -n streamflow-kafka streamflow-kafka-kafka-0 -f | grep -i rebalance
```

---

## Flink Operations

### Check Job Status

**Via REST API:**
```bash
kubectl port-forward -n streamflow-processing svc/flink-jobmanager-rest 8081:8081 &

curl -s http://localhost:8081/jobs | jq '.jobs[] | {id, status}'
```

**Via Flink CLI:**
```bash
kubectl exec -it deployment/flink-jobmanager -n streamflow-processing -- \
  bin/flink list

# Expected output:
# ------------------- Running/Restarting Jobs -------------------
# 25.01.2026 10:00:00 : <job-id> : FraudDetectionJob (RUNNING)
```

### Restart Flink Job

**Graceful restart (with savepoint):**
```bash
# Take savepoint
JOB_ID=$(curl -s http://localhost:8081/jobs | jq -r '.jobs[0].id')
curl -X POST http://localhost:8081/jobs/$JOB_ID/savepoints \
  -H "Content-Type: application/json" \
  -d '{"target-directory": "/opt/flink/savepoints", "cancel-job": true}'

# Wait for savepoint to complete (check response for location)
SAVEPOINT_PATH=<path-from-response>

# Submit job from savepoint
kubectl exec -it deployment/flink-jobmanager -n streamflow-processing -- \
  bin/flink run -s $SAVEPOINT_PATH -d \
  /opt/flink/jobs/fraud-detection.jar
```

**Hard restart (no savepoint, faster):**
```bash
# Cancel job
curl -X PATCH http://localhost:8081/jobs/$JOB_ID?mode=cancel

# Restart Flink deployment
kubectl rollout restart deployment/flink-jobmanager -n streamflow-processing
kubectl rollout restart deployment/flink-taskmanager -n streamflow-processing

# Job will auto-restart from last checkpoint
```

### Checkpoint Recovery

**Check last successful checkpoint:**
```bash
curl -s http://localhost:8081/jobs/$JOB_ID/checkpoints | jq '.latest.completed | {
  id,
  trigger_timestamp: .trigger_timestamp,
  duration,
  state_size
}'
```

**Recover from specific checkpoint:**
```bash
# List checkpoints in persistent storage
kubectl exec -it deployment/flink-jobmanager -n streamflow-processing -- \
  ls -lh /opt/flink/checkpoints/$JOB_ID/

# Restore from checkpoint
kubectl exec -it deployment/flink-jobmanager -n streamflow-processing -- \
  bin/flink run -s /opt/flink/checkpoints/$JOB_ID/chk-12345 -d \
  /opt/flink/jobs/fraud-detection.jar
```

### Scale TaskManagers

**Increase TaskManager replicas:**
```bash
# Edit deployment
kubectl scale deployment flink-taskmanager -n streamflow-processing --replicas=3

# Verify scaling
kubectl get pods -n streamflow-processing -l component=taskmanager

# Flink will automatically redistribute task slots
```

**Adjust in Terraform:**
```hcl
# In infra/flink/terragrunt.hcl
inputs = {
  task_managers = 3  # Increase from 2
  task_slots    = 2  # Total parallelism = 6
}
```

```bash
cd infra/flink
terragrunt apply
```

---

## PostgreSQL Operations

### Check Connection Count

```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  datname,
  COUNT(*) as connections,
  MAX(setting::int) as max_connections
FROM pg_stat_activity
CROSS JOIN pg_settings
WHERE pg_settings.name = 'max_connections'
GROUP BY datname, max_connections
ORDER BY connections DESC;
"
```

**High connection usage (> 80%):**
1. Identify top connection consumers:
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "
   SELECT
     usename,
     application_name,
     COUNT(*) as connections
   FROM pg_stat_activity
   GROUP BY usename, application_name
   ORDER BY connections DESC;
   "
   ```

2. Kill idle connections:
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '30 minutes';
   "
   ```

### Check Table Sizes

```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  schemaname||'.'||tablename as table,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
  pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

### Manual Vacuum

**Analyze table bloat:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  schemaname||'.'||tablename as table,
  n_dead_tup,
  n_live_tup,
  ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
  AND n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
"
```

**Vacuum specific table:**
```bash
# Standard vacuum
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "VACUUM ANALYZE bronze.transactions;"

# Full vacuum (requires exclusive lock, more aggressive)
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "VACUUM FULL bronze.transactions;"
```

**Schedule vacuum during maintenance window:**
```bash
# In maintenance DAG (runs at 03:00 UTC)
# See src/airflow_dags/maintenance_tasks.py
```

### Backup and Restore

**Manual backup (CloudNativePG):**
```bash
# Trigger on-demand backup
kubectl cnpg backup streamflow-postgres -n streamflow-data --backup-name manual-$(date +%Y%m%d-%H%M%S)

# List backups
kubectl get backups -n streamflow-data

# Expected: Backup completes in < 10 minutes
```

**Manual backup (pg_dump):**
```bash
# Dump specific schema
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  pg_dump -U postgres -n bronze -F c -f /tmp/bronze_backup.dump

# Copy to local machine
kubectl cp streamflow-data/streamflow-postgres-1:/tmp/bronze_backup.dump ./bronze_backup_$(date +%Y%m%d).dump
```

**Restore from backup:**
```bash
# Restore schema from pg_dump
kubectl cp ./bronze_backup.dump streamflow-data/streamflow-postgres-1:/tmp/bronze_backup.dump

kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  pg_restore -U postgres -d postgres -n bronze -c /tmp/bronze_backup.dump
```

### Replication Status (N/A for Single-Node)

**Note:** Single-node K3s cluster does not have PostgreSQL replication configured. For multi-node deployments:

```bash
# Check replication lag
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  application_name,
  state,
  sync_state,
  pg_wal_lsn_diff(pg_current_wal_lsn(), replay_lsn) AS lag_bytes,
  EXTRACT(EPOCH FROM (NOW() - reply_time)) as lag_seconds
FROM pg_stat_replication;
"
```

---

## Airflow Operations

### Check DAG Status

**List all DAGs:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list
```

**Check DAG paused status:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list --output json | jq '.[] | {dag_id, is_paused}'
```

**Unpause a DAG:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags unpause bronze_to_silver_pipeline
```

### Clear Failed Tasks

**List failed tasks:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow tasks list bronze_to_silver_pipeline --tree

kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --state failed --dag-id bronze_to_silver_pipeline
```

**Clear task instances (allows retry):**
```bash
# Clear specific task
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow tasks clear bronze_to_silver_pipeline -t transform_bronze_data \
  --start-date 2026-02-06 --end-date 2026-02-06 -y

# Clear entire DAG run
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags backfill bronze_to_silver_pipeline \
  --start-date 2026-02-06 --end-date 2026-02-06 --reset-dagruns -y
```

### Trigger Manual Run

**Trigger DAG with default config:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags trigger bronze_to_silver_pipeline
```

**Trigger with custom config:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags trigger bronze_to_silver_pipeline \
  --conf '{"force_full_refresh": true, "batch_size": 10000}'
```

**Monitor DAG run:**
```bash
# Get latest run ID
RUN_ID=$(kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --dag-id bronze_to_silver_pipeline --limit 1 --output json | jq -r '.[0].run_id')

# Watch run status
watch -n 5 "kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --dag-id bronze_to_silver_pipeline --limit 1"
```

### Restart Airflow Scheduler

```bash
# Restart scheduler deployment
kubectl rollout restart deployment/airflow-scheduler -n streamflow-orchestration

# Verify restart
kubectl rollout status deployment/airflow-scheduler -n streamflow-orchestration

# Check scheduler is picking up DAGs
kubectl logs -n streamflow-orchestration deployment/airflow-scheduler -f --tail=50
```

---

## Alert Response Procedures

### Alert: KafkaConsumerLagHigh

**Severity:** Warning → Critical (if lag > 50,000)

**Symptoms:**
- Consumer lag > 10,000 messages
- Flink processing slower than Kafka ingestion rate

**Diagnosis:**
```bash
# Check consumer lag
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group flink-fraud-detector

# Check Flink backpressure
# Access Flink UI → Running Jobs → Backpressure tab
kubectl port-forward -n streamflow-processing svc/flink-jobmanager-rest 8081:8081
```

**Root Causes:**
1. Flink job slow (operator bottleneck)
2. Insufficient Flink parallelism
3. High event rate spike
4. State access latency

**Resolution:**

**Immediate (< 5 minutes):**
1. Scale up TaskManagers:
   ```bash
   kubectl scale deployment flink-taskmanager -n streamflow-processing --replicas=3
   ```

2. Increase Flink parallelism (restart job with higher parallelism)

**Short-term (< 1 hour):**
1. Check for slow operators in Flink UI (look for high processing time)
2. Optimize slow operators (e.g., reduce state access, batch database writes)

**Long-term:**
1. Tune Flink configuration (increase memory, optimize checkpointing)
2. Optimize fraud detection algorithms (reduce complexity)
3. Consider sharding customers across multiple Flink jobs

**Escalation:**
- If lag continues growing after 30 minutes → Page SRE on-call
- If lag > 100,000 → Page Data Engineering team

---

### Alert: KafkaBrokerDown

**Severity:** Critical

**Symptoms:**
- Kafka broker pod not running
- Producers/consumers unable to connect
- Pipeline completely stopped

**Diagnosis:**
```bash
# Check Kafka pods
kubectl get pods -n streamflow-kafka

# Check broker logs
kubectl logs -n streamflow-kafka streamflow-kafka-kafka-0 --tail=100

# Common errors:
# - "OutOfMemoryError"
# - "Disk full"
# - "Unable to bind to port 9092"
```

**Root Causes:**
1. Kafka pod crashed (OOMKilled)
2. Persistent volume full
3. Node resource exhaustion
4. Configuration error after deployment

**Resolution:**

**Immediate (< 5 minutes):**
1. Restart Kafka pod:
   ```bash
   kubectl delete pod streamflow-kafka-kafka-0 -n streamflow-kafka
   kubectl wait --for=condition=ready pod/streamflow-kafka-kafka-0 -n streamflow-kafka --timeout=300s
   ```

2. If pod won't start (CrashLoopBackOff), check PVC:
   ```bash
   kubectl get pvc -n streamflow-kafka
   kubectl describe pvc data-streamflow-kafka-kafka-0 -n streamflow-kafka
   ```

3. If disk full, delete old log segments:
   ```bash
   # Reduce retention temporarily
   kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
     bin/kafka-configs.sh --bootstrap-server localhost:9092 \
     --entity-type topics --entity-name transactions.raw \
     --alter --add-config retention.ms=86400000  # 1 day
   ```

**Short-term (< 1 hour):**
1. Increase Kafka memory limits:
   ```hcl
   # In infra/kafka/terragrunt.hcl
   kafka_memory_limit = "2Gi"  # Increase from 1Gi
   ```

2. Expand PVC size:
   ```bash
   kubectl edit pvc data-streamflow-kafka-kafka-0 -n streamflow-kafka
   # Increase storage request
   ```

**Long-term:**
1. Implement PVC monitoring and auto-expansion
2. Set up log compaction for topics
3. Archive old Kafka data to object storage

**Escalation:**
- If broker won't start after 15 minutes → Page SRE on-call
- If data loss suspected → Page Data Engineering lead immediately

---

### Alert: FlinkJobNotRunning

**Severity:** Critical

**Symptoms:**
- Flink job state: FAILED, CANCELED, or missing
- No fraud detection processing
- Consumer lag growing rapidly

**Diagnosis:**
```bash
# Check job status
curl -s http://localhost:8081/jobs | jq '.jobs[] | {id, status}'

# Check JobManager logs
kubectl logs -n streamflow-processing deployment/flink-jobmanager --tail=100

# Common errors:
# - "Job submission failed"
# - "Checkpoint timeout"
# - "TaskManager lost"
# - "User code exception"
```

**Root Causes:**
1. Job crashed due to exception
2. Checkpoint timeout
3. Out of memory in TaskManager
4. Kafka connection lost
5. State backend corruption

**Resolution:**

**Immediate (< 5 minutes):**
1. Restart Flink job from last checkpoint:
   ```bash
   kubectl rollout restart deployment/flink-jobmanager -n streamflow-processing
   # Job will auto-restart with last successful checkpoint
   ```

2. If auto-restart fails, check checkpoint directory:
   ```bash
   kubectl exec -it deployment/flink-jobmanager -n streamflow-processing -- \
     ls -lh /opt/flink/checkpoints/
   ```

3. If checkpoints corrupted, restart job from Kafka offset (data reprocessing):
   ```bash
   # Reset Kafka consumer group to earliest offset
   kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
     bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
     --group flink-fraud-detector --reset-offsets --to-earliest --all-topics --execute

   # Restart Flink job (will reprocess all data)
   kubectl rollout restart deployment/flink-jobmanager -n streamflow-processing
   ```

**Short-term (< 1 hour):**
1. Analyze exception stack trace in JobManager logs
2. Fix application bug if user code exception
3. Increase checkpoint timeout if timeout issue:
   ```python
   # In src/flink_jobs/fraud_detector.py
   env.get_checkpoint_config().set_checkpoint_timeout(600000)  # 10 minutes
   ```

**Long-term:**
1. Implement comprehensive exception handling in Flink job
2. Add job monitoring and auto-restart logic
3. Set up state backend backup/recovery

**Escalation:**
- If job won't start after 30 minutes → Page Data Engineering team
- If data reprocessing required → Notify stakeholders of 1-2 hour delay

---

### Alert: FlinkCheckpointFailing

**Severity:** Warning → Critical (if no successful checkpoint in 30 minutes)

**Symptoms:**
- Checkpoints consistently failing
- Warning: "Checkpoint expired before being completed"
- State backend errors

**Diagnosis:**
```bash
# Check checkpoint statistics
curl -s http://localhost:8081/jobs/$JOB_ID/checkpoints | jq '{
  latest_completed: .latest.completed.trigger_timestamp,
  latest_failed: .latest.failed.trigger_timestamp,
  failure_message: .latest.failed.failure_message
}'

# Check state size
curl -s http://localhost:8081/jobs/$JOB_ID/checkpoints | jq '.latest.completed.state_size'

# Check TaskManager logs for state backend errors
kubectl logs -n streamflow-processing -l component=taskmanager --tail=100
```

**Root Causes:**
1. Checkpoint timeout (state too large)
2. State backend disk I/O slow
3. Network issues during state transfer
4. Kafka offset commit failures

**Resolution:**

**Immediate (< 5 minutes):**
1. Increase checkpoint timeout:
   ```bash
   # Restart job with increased timeout
   # Update in src/flink_jobs/fraud_detector.py:
   # env.get_checkpoint_config().set_checkpoint_timeout(900000)  # 15 minutes
   ```

2. Reduce checkpoint frequency:
   ```python
   # From 60 seconds to 120 seconds
   env.enable_checkpointing(120000)
   ```

**Short-term (< 1 hour):**
1. Check state backend disk performance:
   ```bash
   kubectl exec -it deployment/flink-taskmanager-0 -n streamflow-processing -- \
     dd if=/dev/zero of=/opt/flink/state/test bs=1M count=100 conv=fdatasync
   # Should complete in < 5 seconds
   ```

2. Prune old state (reduce state size):
   ```python
   # Reduce state TTL in fraud detector
   # state_ttl = StateTtlConfig.new_builder(Time.hours(24)).build()
   ```

**Long-term:**
1. Migrate to incremental checkpoints (RocksDB):
   ```python
   env.get_state_backend().enable_incremental_checkpointing(True)
   ```

2. Implement state pruning logic (remove old customer data)
3. Monitor state size growth over time

**Escalation:**
- If no successful checkpoint for 1 hour → Page Data Engineering team
- Risk: Job restart will lose 1 hour of stateful data (reprocessing required)

---

### Alert: PostgresHighConnections

**Severity:** Warning → Critical (if > 95% connections)

**Symptoms:**
- Connection pool near exhaustion
- Applications receiving "too many connections" errors
- Airflow tasks failing with connection errors

**Diagnosis:**
```bash
# Check connection count by application
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  usename,
  application_name,
  COUNT(*) as connections,
  MAX(CASE WHEN state = 'idle' THEN 1 ELSE 0 END) as has_idle
FROM pg_stat_activity
GROUP BY usename, application_name
ORDER BY connections DESC;
"
```

**Root Causes:**
1. Connection leak in application code
2. Too many idle connections not released
3. Airflow workers not closing connections
4. Undersized connection pool

**Resolution:**

**Immediate (< 5 minutes):**
1. Kill idle connections:
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "
   SELECT pg_terminate_backend(pid)
   FROM pg_stat_activity
   WHERE state = 'idle'
     AND state_change < NOW() - INTERVAL '10 minutes'
     AND application_name NOT IN ('psql');
   "
   ```

2. Restart Airflow workers (frees connections):
   ```bash
   kubectl rollout restart deployment/airflow-worker -n streamflow-orchestration
   ```

**Short-term (< 1 hour):**
1. Increase PostgreSQL max_connections:
   ```bash
   kubectl edit cluster streamflow-postgres -n streamflow-data
   # Add: max_connections: "200"
   ```

2. Reduce Airflow connection pool size:
   ```bash
   kubectl edit configmap airflow-config -n streamflow-orchestration
   # Set: sql_alchemy_pool_size: 5
   #      sql_alchemy_max_overflow: 10
   ```

**Long-term:**
1. Implement connection pooling (PgBouncer)
2. Add connection monitoring alerts
3. Audit application code for connection leaks
4. Implement automatic connection cleanup

**Escalation:**
- If issue persists after killing idle connections → Page Database team

---

### Alert: PostgresPVCNearlyFull

**Severity:** Warning (> 80% full) → Critical (> 95% full)

**Symptoms:**
- PostgreSQL PVC disk usage high
- Warning: "No space left on device"
- Database writes failing

**Diagnosis:**
```bash
# Check PVC usage
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- df -h /var/lib/postgresql/data

# Check largest tables
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  schemaname||'.'||tablename as table,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname IN ('bronze', 'silver', 'gold')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;
"
```

**Root Causes:**
1. Unbounded data growth in bronze layer
2. Missing data retention policy
3. WAL log accumulation
4. Table bloat from dead tuples

**Resolution:**

**Immediate (< 15 minutes):**
1. Delete old bronze data (safe, source of truth is Kafka):
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "
   DELETE FROM bronze.transactions
   WHERE transaction_time < EXTRACT(EPOCH FROM NOW() - INTERVAL '7 days');
   "
   ```

2. Vacuum to reclaim space:
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "VACUUM FULL bronze.transactions;"
   ```

**Short-term (< 1 hour):**
1. Expand PVC size:
   ```bash
   kubectl edit pvc streamflow-postgres-1 -n streamflow-data
   # Increase storage: 50Gi → 100Gi
   ```

2. Enable data retention policy in Airflow:
   ```python
   # In maintenance DAG
   # Delete bronze data > 7 days old
   # Archive silver data > 30 days to cold storage
   ```

**Long-term:**
1. Implement automated data lifecycle management
2. Archive historical data to object storage (S3/MinIO)
3. Implement table partitioning by date
4. Set up PVC autoscaling

**Escalation:**
- If PVC > 95% full → Page SRE immediately (risk of database downtime)

---

### Alert: HighFraudRate

**Severity:** Warning (> 10% fraud rate) → Investigation required

**Symptoms:**
- Unusually high percentage of transactions flagged as fraud
- Fraud alert volume spike

**Diagnosis:**
```bash
# Check fraud rate
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  COUNT(*) FILTER (WHERE fraud_score >= 0.7) as fraud_alerts,
  COUNT(*) as total_transactions,
  ROUND(100.0 * COUNT(*) FILTER (WHERE fraud_score >= 0.7) / COUNT(*), 2) as fraud_rate
FROM silver.transactions_enriched
WHERE transaction_time > EXTRACT(EPOCH FROM NOW() - INTERVAL '1 hour');
"

# Check which rules are triggering
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "
SELECT
  rule_id,
  COUNT(*) as trigger_count
FROM silver.fraud_alerts
WHERE created_at > NOW() - INTERVAL '1 hour'
GROUP BY rule_id
ORDER BY trigger_count DESC;
"
```

**Root Causes:**
1. Actual fraud attack in progress
2. False positive spike (rule misconfiguration)
3. Data quality issue (bad location data, incorrect timestamps)
4. Load testing in production

**Resolution:**

**Immediate (< 5 minutes):**
1. Check if this is a known test:
   ```bash
   # Check Slack #data-engineering for announcements
   # Check if load test is running
   ps aux | grep generate_events.py
   ```

2. If not a test, escalate to Fraud Team immediately

3. If false positives suspected, check data quality:
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "
   SELECT
     customer_id,
     COUNT(*) as alert_count,
     array_agg(DISTINCT rule_id) as triggered_rules
   FROM silver.fraud_alerts
   WHERE created_at > NOW() - INTERVAL '1 hour'
   GROUP BY customer_id
   ORDER BY alert_count DESC
   LIMIT 10;
   "
   ```

**Short-term (< 1 hour):**
1. If actual fraud, notify Security team
2. If false positives, adjust rule sensitivity:
   ```bash
   # Temporarily increase alert threshold
   # Update config/fraud_rules.yaml: alert_threshold: 0.8
   # Restart Flink job
   ```

**Long-term:**
1. Implement fraud rate baseline monitoring
2. Add rule tuning based on historical false positive analysis
3. Implement manual fraud analyst feedback loop

**Escalation:**
- High fraud rate (> 20%) → Page Security team immediately
- Suspected false positives → Notify Data Engineering and Fraud teams

---

### Alert: PipelineLatencyHigh

**Severity:** Warning (> 5 minutes) → Critical (> 15 minutes)

**Symptoms:**
- End-to-end pipeline latency high
- Delay between Kafka ingestion and Gold layer updates

**Diagnosis:**
```bash
# Check Bronze → Silver latency (Airflow DAG)
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --dag-id bronze_to_silver_pipeline --limit 5

# Check Silver → Gold latency
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --dag-id silver_to_gold_pipeline --limit 5

# Check Flink processing latency
curl -s http://localhost:8081/jobs/$JOB_ID/metrics | grep -i latency
```

**Root Causes:**
1. Airflow task queue backlog
2. PostgreSQL slow queries
3. Flink consumer lag
4. Resource contention (CPU/memory)

**Resolution:**

**Immediate (< 10 minutes):**
1. Check for stuck Airflow tasks:
   ```bash
   kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
     airflow tasks list bronze_to_silver_pipeline --tree
   ```

2. Clear stuck tasks:
   ```bash
   kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
     airflow tasks clear bronze_to_silver_pipeline --yes
   ```

3. Check PostgreSQL for long-running queries:
   ```bash
   kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
     psql -U postgres -c "
   SELECT
     pid,
     now() - pg_stat_activity.query_start AS duration,
     query
   FROM pg_stat_activity
   WHERE state = 'active'
     AND now() - pg_stat_activity.query_start > interval '5 minutes';
   "
   ```

**Short-term (< 1 hour):**
1. Optimize slow SQL queries (add indexes, rewrite queries)
2. Increase Airflow worker concurrency:
   ```bash
   kubectl scale deployment airflow-worker -n streamflow-orchestration --replicas=2
   ```

3. Reduce batch sizes in Airflow DAGs

**Long-term:**
1. Implement incremental processing (only process new data)
2. Add indexes to frequently queried columns
3. Consider switching to streaming architecture (reduce batch dependency)

**Escalation:**
- If latency > 30 minutes → Page Data Engineering team

---

### Alert: AirflowDAGFailure

**Severity:** Warning (single failure) → Critical (3+ consecutive failures)

**Symptoms:**
- Airflow DAG run failed
- Tasks in failed state
- Email notifications sent

**Diagnosis:**
```bash
# Check failed DAG runs
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --state failed --dag-id bronze_to_silver_pipeline

# Check failed task logs
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow tasks logs bronze_to_silver_pipeline <task-id> <execution-date>
```

**Root Causes:**
1. SQL query error (syntax, constraint violation)
2. Database connection timeout
3. External service unavailable (Kafka, PostgreSQL)
4. Application bug in Airflow task code

**Resolution:**

**Immediate (< 10 minutes):**
1. Review task logs for error message
2. If transient error (timeout), clear and retry:
   ```bash
   kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
     airflow tasks clear bronze_to_silver_pipeline -t <task-id> --yes
   ```

3. If SQL error, fix query and manually run DAG:
   ```bash
   kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
     airflow dags trigger bronze_to_silver_pipeline --conf '{"retry": true}'
   ```

**Short-term (< 1 hour):**
1. Fix application bug in DAG code
2. Deploy updated DAG:
   ```bash
   # Update src/airflow_dags/bronze_to_silver.py
   # Restart Airflow to reload DAG
   kubectl rollout restart deployment/airflow-scheduler -n streamflow-orchestration
   ```

**Long-term:**
1. Add retry logic with exponential backoff
2. Implement comprehensive error handling
3. Add data quality checks before task execution
4. Set up DAG testing in CI/CD

**Escalation:**
- 3+ consecutive failures → Page Data Engineering on-call

---

## Scaling Guide

**Note:** Single-node K3s cluster has resource constraints. Scaling is limited to vertical scaling within node capacity.

### Current Resource Allocation

| Namespace | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| streamflow-kafka | 1 core | 2 cores | 2 GB | 3 GB |
| streamflow-processing | 1 core | 2 cores | 2 GB | 3 GB |
| streamflow-data | 500m | 1 core | 1 GB | 2 GB |
| streamflow-orchestration | 500m | 1 core | 1 GB | 2 GB |
| streamflow-monitoring | 500m | 1 core | 1 GB | 2 GB |
| **Total** | **3.5 cores** | **8 cores** | **7 GB** | **12 GB** |

**Node Capacity:** 4 CPU, 9.7 GB RAM
**Available for scaling:** ~0.5 CPU, ~2.7 GB RAM

### Vertical Scaling Procedures

**Scale Kafka:**
```bash
cd infra/kafka
# Edit terragrunt.hcl
# kafka_memory_limit = "2Gi"  # Increase
terragrunt apply
```

**Scale Flink:**
```bash
cd infra/flink
# Edit terragrunt.hcl
# taskmanager_memory = "2Gi"  # Increase
# task_managers = 2  # Do not increase (resource constrained)
terragrunt apply
```

**Scale PostgreSQL:**
```bash
kubectl edit cluster streamflow-postgres -n streamflow-data
# Edit resources.limits.memory: 3Gi
```

### Horizontal Scaling (Multi-Node)

For production deployments, migrate to multi-node K3s or managed Kubernetes:

1. Add worker nodes to K3s cluster
2. Update resource requests/limits
3. Increase replication factors:
   - Kafka: replication_factor = 3
   - PostgreSQL: replicas = 3
   - Flink: task_managers = 5+

---

## Backup and Recovery

### Automated Backups

**PostgreSQL (CloudNativePG):**
- Daily backups at 02:00 UTC
- Retention: 7 days
- Location: PVC `/backups/`

**Kafka (N/A):**
- Bronze layer in PostgreSQL serves as archive
- Kafka retention: 3 days

### Manual Backup Procedures

**Full PostgreSQL backup:**
```bash
# Create on-demand backup
kubectl cnpg backup streamflow-postgres -n streamflow-data --backup-name manual-$(date +%Y%m%d)

# Wait for completion
kubectl get backups -n streamflow-data -w
```

**Export Gold layer for reporting:**
```bash
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  pg_dump -U postgres -n gold -F c -f /tmp/gold_export.dump

kubectl cp streamflow-data/streamflow-postgres-1:/tmp/gold_export.dump \
  ./gold_export_$(date +%Y%m%d).dump
```

### Recovery Procedures

**Recover PostgreSQL from backup:**
```bash
# List available backups
kubectl get backups -n streamflow-data

# Restore from backup
kubectl cnpg restore streamflow-postgres -n streamflow-data \
  --backup-name <backup-name>
```

**Reprocess Kafka data (disaster recovery):**
```bash
# Reset Flink consumer group to beginning
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group flink-fraud-detector --reset-offsets --to-earliest --all-topics --execute

# Truncate target tables
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "TRUNCATE silver.transactions_enriched CASCADE;"

# Restart Flink job (will reprocess all Kafka data)
kubectl rollout restart deployment/flink-jobmanager -n streamflow-processing
```

---

## Maintenance Windows

### Daily Maintenance (03:00 UTC)

**Airflow DAG:** `maintenance_tasks`

**Tasks:**
1. Vacuum PostgreSQL tables
2. Delete old Bronze data (> 7 days)
3. Refresh materialized views in Gold layer
4. Backup PostgreSQL
5. Cleanup old Airflow logs

**Expected duration:** 20-30 minutes

**Monitor:**
```bash
kubectl exec -it deployment/airflow-scheduler -n streamflow-orchestration -- \
  airflow dags list-runs --dag-id maintenance_tasks --limit 5
```

### Weekly Maintenance (Sunday 02:00 UTC)

**Manual tasks:**
1. Review alert history
2. Analyze fraud detection accuracy
3. Tune fraud rule thresholds
4. Review resource utilization trends
5. Plan capacity upgrades

---

## Emergency Procedures

### Full Platform Restart

**Use only as last resort (causes 5-10 minutes downtime)**

```bash
# 1. Stop data ingestion
# Pause event generator if running
pkill -f generate_events.py

# 2. Drain Kafka consumer lag (wait for Flink to catch up)
watch kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --describe --group flink-fraud-detector

# 3. Stop Flink jobs (gracefully)
curl -X POST http://localhost:8081/jobs/$JOB_ID/savepoints \
  -H "Content-Type: application/json" \
  -d '{"target-directory": "/opt/flink/savepoints", "cancel-job": true}'

# 4. Restart all deployments in order
kubectl rollout restart deployment -n streamflow-kafka
kubectl rollout restart deployment -n streamflow-processing
kubectl rollout restart statefulset -n streamflow-data
kubectl rollout restart deployment -n streamflow-orchestration

# 5. Wait for all pods to be ready
kubectl wait --for=condition=ready pods --all -n streamflow-kafka --timeout=300s
kubectl wait --for=condition=ready pods --all -n streamflow-processing --timeout=300s
kubectl wait --for=condition=ready pods --all -n streamflow-data --timeout=300s
kubectl wait --for=condition=ready pods --all -n streamflow-orchestration --timeout=300s

# 6. Verify services are healthy (run health checks from section 1)

# 7. Resume data ingestion
python scripts/generate_events.py --rate 100 --duration 3600
```

### Data Recovery (Bronze Layer Corruption)

```bash
# 1. Stop Flink ingestion
kubectl delete deployment flink-jobmanager -n streamflow-processing

# 2. Truncate Bronze tables
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "TRUNCATE bronze.transactions CASCADE;"

# 3. Replay from Kafka (if data available)
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
  --group flink-fraud-detector --reset-offsets --to-earliest --topic transactions.raw --execute

# 4. Restart Flink to reprocess
kubectl apply -f infra/flink/fraud-detection-job.yaml

# 5. Monitor reprocessing progress
watch kubectl exec -it streamflow-postgres-1 -n streamflow-data -- \
  psql -U postgres -c "SELECT COUNT(*) FROM bronze.transactions;"
```

---

## Appendix: Useful Commands

### Kubernetes

```bash
# Get all resources in namespace
kubectl get all -n streamflow-kafka

# Describe pod for detailed info
kubectl describe pod <pod-name> -n <namespace>

# Get events (useful for debugging)
kubectl get events -n <namespace> --sort-by='.lastTimestamp'

# Execute command in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/bash

# View resource usage
kubectl top nodes
kubectl top pods -A

# Force delete stuck pod
kubectl delete pod <pod-name> -n <namespace> --grace-period=0 --force
```

### PostgreSQL

```bash
# Connect to database
kubectl exec -it streamflow-postgres-1 -n streamflow-data -- psql -U postgres

# Common psql commands:
# \l          - List databases
# \dn         - List schemas
# \dt schema.* - List tables in schema
# \d+ table   - Describe table
# \x          - Toggle expanded output
# \timing     - Toggle query timing
# \q          - Quit
```

### Kafka

```bash
# Produce test message
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic transactions.raw

# Consume messages
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic transactions.raw --from-beginning

# Delete topic (caution!)
kubectl exec -it streamflow-kafka-kafka-0 -n streamflow-kafka -- \
  bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic <topic-name>
```

### Monitoring

```bash
# Query Prometheus
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-prometheus 9090:9090
# Access: http://localhost:9090

# View Grafana
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-grafana 3000:80
# Access: http://localhost:3000

# Check Alertmanager
kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-alertmanager 9093:9093
# Access: http://localhost:9093
```

---

## Document Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2026-02-06 | Platform Team | Initial runbook created |

---

## Support

For questions or issues not covered in this runbook:

- **Slack:** #streamflow-support
- **PagerDuty:** StreamFlow Analytics On-Call
- **Documentation:** [SETUP_GUIDE.md](SETUP_GUIDE.md), [FRAUD_DETECTION.md](FRAUD_DETECTION.md)
- **Wiki:** https://wiki.company.com/streamflow

**On-Call Schedule:** https://company.pagerduty.com/schedules/streamflow
