# -----------------------------------------------------------------------------
# StreamFlow Analytics - Flink Kubernetes Operator Module
# Deploys the Apache Flink Kubernetes Operator via Helm
# Enables declarative FlinkDeployment and FlinkSessionJob CRDs
# -----------------------------------------------------------------------------

terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.12.0"
    }
  }
}

# ---------------------------------------------------------------------------
# Flink Kubernetes Operator (Helm)
# ---------------------------------------------------------------------------
resource "helm_release" "flink_operator" {
  name             = "flink-operator"
  repository       = "https://downloads.apache.org/flink/flink-kubernetes-operator-1.10.0/"
  chart            = "flink-kubernetes-operator"
  version          = var.chart_version
  namespace        = var.namespace
  create_namespace = false

  # Operator pod resource constraints (K3s-friendly)
  set {
    name  = "resources.requests.memory"
    value = "128Mi"
  }

  set {
    name  = "resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "resources.limits.memory"
    value = "256Mi"
  }

  set {
    name  = "resources.limits.cpu"
    value = "200m"
  }

  # Webhook configuration
  set {
    name  = "webhook.create"
    value = "true"
  }

  # Watch only the target namespace to reduce RBAC scope
  set {
    name  = "watchNamespaces[0]"
    value = var.namespace
  }
}
