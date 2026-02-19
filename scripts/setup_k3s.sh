#!/usr/bin/env bash
# StreamFlow Analytics — One-time K3s Node Preparation
# Creates namespaces, installs operators, and prepares the cluster.
#
# Usage: ./scripts/setup_k3s.sh

set -euo pipefail

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }

log_info "=== StreamFlow Analytics — K3s Setup ==="

# 1. Create namespaces
log_info "Creating namespaces..."
for ns in streamflow-kafka streamflow-processing streamflow-data streamflow-orchestration streamflow-monitoring; do
    kubectl create namespace "$ns" --dry-run=client -o yaml | kubectl apply -f -
done
log_ok "Namespaces created"

# 2. Install Strimzi Kafka Operator
log_info "Installing Strimzi Kafka Operator..."
kubectl create namespace strimzi --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -f "https://strimzi.io/install/latest?namespace=streamflow-kafka" -n streamflow-kafka 2>/dev/null || true
log_ok "Strimzi applied"

# 3. Install Flink Kubernetes Operator
log_info "Installing Flink Kubernetes Operator..."
if command -v helm &>/dev/null; then
    helm repo add flink-operator-repo https://downloads.apache.org/flink/flink-kubernetes-operator-1.10.0/ 2>/dev/null || true
    helm repo update 2>/dev/null || true
    helm upgrade --install flink-kubernetes-operator flink-operator-repo/flink-kubernetes-operator \
        --namespace streamflow-processing \
        --set webhook.create=false \
        --wait --timeout 120s 2>/dev/null || log_info "Flink operator may already be installed"
    log_ok "Flink Operator installed"
else
    log_info "Helm not found — install Flink Operator manually"
fi

# 4. Install CloudNativePG Operator
log_info "Installing CloudNativePG Operator..."
kubectl apply --server-side -f https://raw.githubusercontent.com/cloudnative-pg/cloudnative-pg/release-1.24/releases/cnpg-1.24.1.yaml 2>/dev/null || true
log_ok "CloudNativePG applied"

# 5. Create Flink ServiceAccount
log_info "Creating Flink ServiceAccount..."
kubectl create serviceaccount flink -n streamflow-processing --dry-run=client -o yaml | kubectl apply -f -
kubectl create clusterrolebinding flink-role-binding \
    --clusterrole=edit \
    --serviceaccount=streamflow-processing:flink \
    --dry-run=client -o yaml | kubectl apply -f -
log_ok "Flink SA + RoleBinding created"

# 6. Install Airflow via Helm
log_info "Installing Airflow..."
if command -v helm &>/dev/null; then
    helm repo add apache-airflow https://airflow.apache.org 2>/dev/null || true
    helm repo update 2>/dev/null || true
    log_ok "Airflow Helm repo added (deploy via Terraform or 'helm install')"
else
    log_info "Helm not found — install Airflow manually"
fi

echo ""
log_ok "=== K3s setup complete ==="
echo ""
echo "Next steps:"
echo "  1. Build + import images:  ./scripts/deploy.sh images"
echo "  2. Deploy pipeline:        ./scripts/deploy.sh all"
echo "  3. Check status:           ./scripts/deploy.sh status"
