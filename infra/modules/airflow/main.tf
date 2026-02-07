# -----------------------------------------------------------------------------
# StreamFlow Analytics - Apache Airflow Module
# Deploys Airflow via the official Helm chart with LocalExecutor
# Optimized for K3s single-node development environments
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
# Apache Airflow (Helm)
# ---------------------------------------------------------------------------
resource "helm_release" "airflow" {
  name             = "airflow"
  repository       = "https://airflow.apache.org"
  chart            = "airflow"
  version          = var.chart_version
  namespace        = var.namespace
  create_namespace = false
  timeout          = 600

  values = [
    file("${path.module}/values.yaml")
  ]

  # Override executor from values if variable differs from default
  set {
    name  = "executor"
    value = var.executor
  }

  set {
    name  = "webserver.replicas"
    value = var.webserver_replicas
  }

  # Ensure Airflow uses its bundled PostgreSQL for metadata
  set {
    name  = "postgresql.enabled"
    value = "true"
  }

  # Disable components not needed for LocalExecutor
  set {
    name  = "flower.enabled"
    value = "false"
  }

  set {
    name  = "triggerer.enabled"
    value = "false"
  }

  set {
    name  = "pgbouncer.enabled"
    value = "false"
  }

  set {
    name  = "workers.enabled"
    value = "false"
  }
}
