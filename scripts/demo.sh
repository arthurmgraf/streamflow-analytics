#!/usr/bin/env bash
# StreamFlow Analytics — Full Pipeline Demo
# One-command demo: setup → build → deploy → verify → show results
#
# Usage: ./scripts/demo.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }

echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║     StreamFlow Analytics — Live Demo          ║"
echo "  ║     Real-time Fraud Detection Pipeline        ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Build + Import + Deploy
log_info "Step 1: Full deployment..."
"$SCRIPT_DIR/deploy.sh" all

echo ""
log_info "Step 2: Waiting for pipeline to stabilize (60s)..."
sleep 60

# Step 3: Verify data flow
log_info "Step 3: Verifying data flow..."

PG_POD=$(kubectl get pods -n streamflow-data -l role=primary -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [[ -n "$PG_POD" ]]; then
    echo ""
    log_info "=== Bronze Layer (raw from Kafka) ==="
    kubectl exec -n streamflow-data "$PG_POD" -- psql -U streamflow -c \
        "SELECT count(*) as total_raw, max(ingested_at) as latest FROM bronze.raw_transactions;" 2>/dev/null || log_warn "Bronze query failed"

    echo ""
    log_info "=== Silver Layer (cleaned by dbt) ==="
    kubectl exec -n streamflow-data "$PG_POD" -- psql -U streamflow -c \
        "SELECT count(*) as total_clean, count(*) filter (where is_fraud) as fraud_count FROM silver.stg_transactions;" 2>/dev/null || log_warn "Silver query failed"

    echo ""
    log_info "=== Gold Layer (marts by dbt) ==="
    kubectl exec -n streamflow-data "$PG_POD" -- psql -U streamflow -c \
        "SELECT count(*) as total_facts FROM gold.fct_transactions;" 2>/dev/null || log_warn "Gold query failed"

    echo ""
    log_info "=== Fraud Summary ==="
    kubectl exec -n streamflow-data "$PG_POD" -- psql -U streamflow -c \
        "SELECT date_key, total_alerts, total_txns, round(fraud_rate::numeric, 4) as fraud_rate, top_rule FROM gold.agg_daily_fraud ORDER BY date_key DESC LIMIT 5;" 2>/dev/null || log_warn "Fraud summary query failed"
else
    log_warn "PostgreSQL pod not found — data verification skipped"
fi

echo ""
log_info "Step 4: Port-forward URLs..."
echo ""
echo "  Airflow UI:     kubectl port-forward svc/airflow-webserver -n streamflow-orchestration 8080:8080"
echo "  Flink UI:       kubectl port-forward svc/fraud-detector-rest -n streamflow-processing 8081:8081"
echo ""

echo -e "${GREEN}"
echo "  ╔═══════════════════════════════════════════════╗"
echo "  ║            Demo Complete!                     ║"
echo "  ║                                               ║"
echo "  ║  Generator → Kafka → Flink → PostgreSQL       ║"
echo "  ║  Airflow + dbt (Cosmos) → Silver → Gold       ║"
echo "  ╚═══════════════════════════════════════════════╝"
echo -e "${NC}"
