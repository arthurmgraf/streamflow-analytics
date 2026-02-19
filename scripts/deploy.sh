#!/usr/bin/env bash
# StreamFlow Analytics — Production Deploy Script v2
# Full pipeline: build images → import to K3s → deploy manifests → verify
#
# Usage:
#   ./scripts/deploy.sh all          # Full deploy (build + import + apply + smoke)
#   ./scripts/deploy.sh argocd       # Deploy via ArgoCD sync
#   ./scripts/deploy.sh kubectl      # Deploy via kubectl apply (no image build)
#   ./scripts/deploy.sh images       # Build + import images only
#   ./scripts/deploy.sh status       # Check deployment status
#   ./scripts/deploy.sh smoke        # Run smoke tests

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

TAG="${TAG:-latest}"
SSH_HOST="${SSH_HOST:-}"

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

    log_ok "Prerequisites OK"
}

build_images() {
    log_info "Building Docker images (tag: $TAG)..."

    if ! command -v docker &>/dev/null; then
        log_error "Docker not found. Install Docker to build images."
        exit 1
    fi

    "$SCRIPT_DIR/build_images.sh" "$TAG"
    log_ok "All 3 images built"
}

import_images() {
    log_info "Importing images to K3s..."

    if [[ -n "$SSH_HOST" ]]; then
        "$SCRIPT_DIR/import_images.sh" "$TAG" "$SSH_HOST"
    else
        "$SCRIPT_DIR/import_images.sh" "$TAG"
    fi
    log_ok "Images imported to K3s"
}

deploy_argocd() {
    log_info "Deploying via ArgoCD (GitOps)..."

    if ! kubectl get namespace argocd &>/dev/null 2>&1; then
        log_error "ArgoCD namespace not found. Install ArgoCD first."
        exit 1
    fi

    kubectl apply -f "$PROJECT_DIR/k8s/argocd/application.yaml"
    log_ok "ArgoCD Application created/updated"

    if command -v argocd &>/dev/null; then
        argocd app wait streamflow-analytics --timeout 300 || true
    else
        log_warn "argocd CLI not installed — check dashboard for sync status"
    fi

    log_ok "ArgoCD deploy complete"
}

deploy_kubectl() {
    log_info "Deploying via kubectl (direct apply)..."

    log_info "[1/6] Deploying infrastructure with Terragrunt..."
    if command -v terragrunt &>/dev/null; then
        cd "$PROJECT_DIR/infra/environments/dev"
        terragrunt run-all init --terragrunt-non-interactive 2>/dev/null
        terragrunt run-all apply --terragrunt-non-interactive -auto-approve
        cd "$PROJECT_DIR"
        log_ok "Infrastructure deployed"
    else
        log_warn "Terragrunt not found — assumes namespaces already exist"
    fi

    log_info "[2/6] Applying security policies..."
    kubectl apply -f "$PROJECT_DIR/k8s/security/network-policies.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/security/pod-disruption-budgets.yaml"
    log_ok "Security policies applied"

    log_info "[3/6] Applying Kafka topics..."
    kubectl apply -f "$PROJECT_DIR/k8s/kafka/kafka-topics.yaml"
    log_ok "Kafka topics applied"

    log_info "[4/6] Deploying Flink jobs..."
    kubectl apply -f "$PROJECT_DIR/k8s/flink/transaction-processor.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/flink/fraud-detector.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/flink/realtime-aggregator.yaml"
    log_ok "Flink jobs deployed (PyFlink mode)"

    log_info "[5/6] Deploying transaction generator..."
    kubectl apply -f "$PROJECT_DIR/k8s/generator/deployment.yaml"
    log_ok "Generator deployed"

    log_info "[6/6] Applying monitoring..."
    kubectl apply -f "$PROJECT_DIR/k8s/monitoring/service-monitors.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/monitoring/alerting-rules.yaml"
    kubectl apply -f "$PROJECT_DIR/k8s/monitoring/slo-rules.yaml"
    log_ok "Monitoring applied"

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

    echo "=== Generator ==="
    kubectl get deployment -n streamflow-kafka transaction-generator 2>/dev/null || log_warn "No generator found"
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

    log_info "Checking Generator..."
    local gen_ready
    gen_ready=$(kubectl get deployment -n streamflow-kafka transaction-generator -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    if [[ "$gen_ready" -ge 1 ]]; then
        log_ok "Generator: Running ($gen_ready replicas)"
    else
        log_warn "Generator: not ready"
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
    echo "StreamFlow Analytics Deploy Script v2"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  all        Full deploy: build + import + kubectl + smoke"
    echo "  images     Build Docker images + import to K3s"
    echo "  argocd     Deploy via ArgoCD (GitOps)"
    echo "  kubectl    Deploy via kubectl (no image build)"
    echo "  status     Show deployment status"
    echo "  smoke      Run post-deploy smoke tests"
    echo ""
    echo "Environment:"
    echo "  TAG=v1.0   Image tag (default: latest)"
    echo "  SSH_HOST=  Remote K3s host for image import"
    echo ""
    echo "Examples:"
    echo "  $0 all                                    # Local K3s full deploy"
    echo "  TAG=v1.0 SSH_HOST=user@host $0 all        # Remote K3s deploy"
    echo "  $0 images                                  # Build + import only"
    echo "  $0 status                                  # Check current state"
}

case "${1:-help}" in
    all)
        check_prerequisites
        build_images
        import_images
        deploy_kubectl
        run_smoke_test
        show_status
        ;;
    images)
        build_images
        import_images
        ;;
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
    *)
        show_usage
        ;;
esac
