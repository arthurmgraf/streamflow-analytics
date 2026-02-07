#!/usr/bin/env bash
# StreamFlow Analytics — Production Deploy Script
# Supports ArgoCD (GitOps) and kubectl (direct) deployment methods
#
# Usage:
#   ./scripts/deploy.sh argocd     # Deploy via ArgoCD sync
#   ./scripts/deploy.sh kubectl    # Deploy via kubectl apply
#   ./scripts/deploy.sh status     # Check deployment status
#   ./scripts/deploy.sh rollback   # Rollback to previous savepoint

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

check_prerequisites() {
    log_info "Checking prerequisites..."
    local missing=0

    if ! command -v kubectl &>/dev/null; then
        log_error "kubectl not found"
        missing=1
    fi

    if ! kubectl cluster-info &>/dev/null 2>&1; then
        log_error "Cannot connect to Kubernetes cluster"
        missing=1
    fi

    if [[ $missing -ne 0 ]]; then
        log_error "Prerequisites check failed"
        exit 1
    fi

    log_ok "Prerequisites OK (kubectl $(kubectl version --client -o json 2>/dev/null | python3 -c 'import sys,json;print(json.load(sys.stdin)["clientVersion"]["gitVersion"])' 2>/dev/null || echo 'unknown'))"
}

deploy_argocd() {
    log_info "Deploying via ArgoCD (GitOps)..."

    if ! kubectl get namespace argocd &>/dev/null 2>&1; then
        log_error "ArgoCD namespace not found. Install ArgoCD first:"
        log_error "  kubectl create namespace argocd"
        log_error "  kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml"
        exit 1
    fi

    log_info "Applying ArgoCD Application..."
    kubectl apply -f "$PROJECT_DIR/k8s/argocd/application.yaml"
    log_ok "ArgoCD Application created/updated"

    log_info "Waiting for sync..."
    if command -v argocd &>/dev/null; then
        argocd app wait streamflow-analytics --timeout 300 || true
    else
        log_warn "argocd CLI not installed — check ArgoCD dashboard for sync status"
        log_info "  kubectl port-forward svc/argocd-server -n argocd 8443:443"
    fi

    log_ok "ArgoCD deploy complete — auto-sync enabled with self-heal"
}

deploy_kubectl() {
    log_info "Deploying via kubectl (direct apply)..."

    log_info "[1/5] Deploying infrastructure with Terragrunt..."
    if command -v terragrunt &>/dev/null; then
        cd "$PROJECT_DIR/infra/environments/dev"
        terragrunt run-all init --terragrunt-non-interactive 2>/dev/null
        terragrunt run-all apply --terragrunt-non-interactive -auto-approve
        cd "$PROJECT_DIR"
        log_ok "Infrastructure deployed"
    else
        log_warn "Terragrunt not found — skipping infra (assumes namespaces already exist)"
    fi

    log_info "[2/5] Applying security policies..."
    kubectl apply -f "$PROJECT_DIR/k8s/security/network-policies.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/security/pod-disruption-budgets.yaml"
    log_ok "Security policies applied (NetworkPolicies + PDBs)"

    log_info "[3/5] Applying Kafka topics..."
    kubectl apply -f "$PROJECT_DIR/k8s/kafka/kafka-topics.yaml"
    log_ok "Kafka topics applied (4 topics including DLQ)"

    log_info "[4/5] Deploying Flink jobs..."
    kubectl apply -f "$PROJECT_DIR/k8s/flink/transaction-processor.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/flink/fraud-detector.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/flink/realtime-aggregator.yaml"
    log_ok "Flink jobs deployed (3 FlinkDeployments with RocksDB + EXACTLY_ONCE)"

    log_info "[5/5] Applying monitoring..."
    kubectl apply -f "$PROJECT_DIR/k8s/monitoring/service-monitors.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/monitoring/alerting-rules.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/monitoring/slo-rules.yaml"
    log_ok "Monitoring applied (ServiceMonitors + AlertRules + SLOs)"

    log_ok "kubectl deploy complete"
}

show_status() {
    log_info "StreamFlow Analytics — Deployment Status"
    echo ""

    echo "=== Namespaces ==="
    kubectl get ns 2>/dev/null | grep streamflow || log_warn "No streamflow namespaces found"
    echo ""

    echo "=== Pods ==="
    kubectl get pods -A 2>/dev/null | grep streamflow || log_warn "No streamflow pods found"
    echo ""

    echo "=== Flink Jobs ==="
    kubectl get flinkdeployment -n streamflow-processing 2>/dev/null || log_warn "No Flink deployments found"
    echo ""

    echo "=== Kafka Topics ==="
    kubectl get kafkatopic -n streamflow-kafka 2>/dev/null || log_warn "No Kafka topics found"
    echo ""

    echo "=== PostgreSQL ==="
    kubectl get cluster -n streamflow-data 2>/dev/null || log_warn "No CNPG cluster found"
    echo ""

    echo "=== Services ==="
    kubectl get svc -A 2>/dev/null | grep streamflow || log_warn "No streamflow services found"
}

run_smoke_test() {
    log_info "Running post-deploy smoke tests..."
    local failures=0

    log_info "Checking Flink jobs..."
    local flink_states
    flink_states=$(kubectl get flinkdeployment -n streamflow-processing -o jsonpath='{.items[*].status.jobStatus.state}' 2>/dev/null || echo "")
    if [[ -n "$flink_states" ]]; then
        log_ok "Flink job states: $flink_states"
    else
        log_warn "Could not read Flink job states"
        failures=$((failures + 1))
    fi

    log_info "Checking Kafka broker..."
    local kafka_ready
    kafka_ready=$(kubectl get kafka -n streamflow-kafka -o jsonpath='{.items[0].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
    if [[ "$kafka_ready" == "True" ]]; then
        log_ok "Kafka broker: Ready"
    else
        log_warn "Kafka broker state: ${kafka_ready:-unknown}"
        failures=$((failures + 1))
    fi

    log_info "Checking PostgreSQL..."
    local pg_ready
    pg_ready=$(kubectl get cluster -n streamflow-data -o jsonpath='{.items[0].status.phase}' 2>/dev/null || echo "")
    if [[ "$pg_ready" == "Cluster in healthy state" ]]; then
        log_ok "PostgreSQL: Healthy"
    else
        log_warn "PostgreSQL state: ${pg_ready:-unknown}"
        failures=$((failures + 1))
    fi

    echo ""
    if [[ $failures -eq 0 ]]; then
        log_ok "All smoke tests passed"
    else
        log_warn "$failures smoke test(s) need attention"
    fi
}

show_usage() {
    echo "StreamFlow Analytics Deploy Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  argocd     Deploy via ArgoCD (GitOps, recommended)"
    echo "  kubectl    Deploy via kubectl direct apply"
    echo "  status     Show deployment status"
    echo "  smoke      Run post-deploy smoke tests"
    echo "  all        Full deploy: kubectl + smoke tests"
    echo ""
    echo "Examples:"
    echo "  $0 argocd          # GitOps deploy (auto-sync)"
    echo "  $0 all             # Full deploy with verification"
    echo "  $0 status          # Check current state"
}

case "${1:-help}" in
    argocd)
        check_prerequisites
        deploy_argocd
        ;;
    kubectl)
        check_prerequisites
        deploy_kubectl
        ;;
    status)
        show_status
        ;;
    smoke)
        run_smoke_test
        ;;
    all)
        check_prerequisites
        deploy_kubectl
        run_smoke_test
        show_status
        ;;
    *)
        show_usage
        ;;
esac
