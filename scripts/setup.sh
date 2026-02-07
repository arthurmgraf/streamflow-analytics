#!/usr/bin/env bash
# StreamFlow Analytics — Initial cluster bootstrap
# Run on the K3s node to install prerequisites

set -euo pipefail

echo "=== StreamFlow Analytics Setup ==="
echo "Target: K3s single-node cluster"
echo ""

# 1. Verify K3s is running
echo "[1/5] Checking K3s..."
if ! kubectl cluster-info &>/dev/null; then
    echo "ERROR: K3s is not running or kubectl is not configured"
    exit 1
fi
echo "  K3s is running"

# 2. Install Terraform (if not present)
echo "[2/5] Checking Terraform..."
if ! command -v terraform &>/dev/null; then
    echo "  Installing Terraform..."
    curl -fsSL https://releases.hashicorp.com/terraform/1.7.5/terraform_1.7.5_linux_amd64.zip -o /tmp/terraform.zip
    unzip -o /tmp/terraform.zip -d /usr/local/bin/
    rm /tmp/terraform.zip
fi
echo "  Terraform $(terraform version -json | python3 -c 'import sys,json;print(json.load(sys.stdin)["terraform_version"])')"

# 3. Install Terragrunt (if not present)
echo "[3/5] Checking Terragrunt..."
if ! command -v terragrunt &>/dev/null; then
    echo "  Installing Terragrunt..."
    curl -fsSL https://github.com/gruntwork-io/terragrunt/releases/latest/download/terragrunt_linux_amd64 -o /usr/local/bin/terragrunt
    chmod +x /usr/local/bin/terragrunt
fi
echo "  Terragrunt $(terragrunt --version | head -1)"

# 4. Deploy infrastructure
echo "[4/5] Deploying infrastructure with Terragrunt..."
cd "$(dirname "$0")/../infra/environments/dev"
terragrunt run-all init --terragrunt-non-interactive
terragrunt run-all apply --terragrunt-non-interactive -auto-approve

# 5. Apply K8s manifests
echo "[5/5] Applying K8s manifests..."
cd "$(dirname "$0")/.."
kubectl apply -f k8s/kafka/kafka-topics.yaml
kubectl apply -f k8s/flink/
kubectl apply -f k8s/monitoring/

echo ""
echo "=== Setup Complete ==="
echo "Verify with: kubectl get pods -A | grep streamflow"
echo "Grafana: kubectl port-forward -n streamflow-monitoring svc/kube-prometheus-stack-grafana 3000:80"
echo "Airflow: kubectl port-forward -n streamflow-orchestration svc/airflow-webserver 8080:8080"
