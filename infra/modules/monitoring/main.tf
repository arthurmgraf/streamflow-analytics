# -----------------------------------------------------------------------------
# StreamFlow Analytics - Monitoring Module
# Deploys kube-prometheus-stack via Helm (Prometheus + Grafana + AlertManager)
# Resource-constrained configuration for K3s environments
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
# kube-prometheus-stack (Helm)
# Includes: Prometheus, Grafana, AlertManager, node-exporter, kube-state-metrics
# ---------------------------------------------------------------------------
resource "helm_release" "kube_prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  version          = var.chart_version
  namespace        = var.namespace
  create_namespace = false
  timeout          = 600

  # ---------------------------------------------------------------------------
  # Prometheus
  # ---------------------------------------------------------------------------
  set {
    name  = "prometheus.enabled"
    value = "true"
  }

  set {
    name  = "prometheus.prometheusSpec.resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "prometheus.prometheusSpec.resources.requests.memory"
    value = "256Mi"
  }

  set {
    name  = "prometheus.prometheusSpec.resources.limits.cpu"
    value = "500m"
  }

  set {
    name  = "prometheus.prometheusSpec.resources.limits.memory"
    value = "512Mi"
  }

  # Retention - keep 7 days of metrics
  set {
    name  = "prometheus.prometheusSpec.retention"
    value = "7d"
  }

  # Storage - 10Gi persistent volume
  set {
    name  = "prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage"
    value = "10Gi"
  }

  # Service monitor selector - match all namespaces
  set {
    name  = "prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  set {
    name  = "prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues"
    value = "false"
  }

  # ---------------------------------------------------------------------------
  # Grafana
  # ---------------------------------------------------------------------------
  set {
    name  = "grafana.enabled"
    value = "true"
  }

  set_sensitive {
    name  = "grafana.adminPassword"
    value = var.grafana_admin_password
  }

  set {
    name  = "grafana.resources.requests.cpu"
    value = "50m"
  }

  set {
    name  = "grafana.resources.requests.memory"
    value = "128Mi"
  }

  set {
    name  = "grafana.resources.limits.cpu"
    value = "200m"
  }

  set {
    name  = "grafana.resources.limits.memory"
    value = "256Mi"
  }

  # Grafana persistence
  set {
    name  = "grafana.persistence.enabled"
    value = "true"
  }

  set {
    name  = "grafana.persistence.size"
    value = "5Gi"
  }

  # Default dashboards
  set {
    name  = "grafana.defaultDashboardsEnabled"
    value = "true"
  }

  # ---------------------------------------------------------------------------
  # AlertManager
  # ---------------------------------------------------------------------------
  set {
    name  = "alertmanager.enabled"
    value = "true"
  }

  set {
    name  = "alertmanager.alertmanagerSpec.resources.requests.cpu"
    value = "25m"
  }

  set {
    name  = "alertmanager.alertmanagerSpec.resources.requests.memory"
    value = "64Mi"
  }

  set {
    name  = "alertmanager.alertmanagerSpec.resources.limits.cpu"
    value = "100m"
  }

  set {
    name  = "alertmanager.alertmanagerSpec.resources.limits.memory"
    value = "128Mi"
  }

  # AlertManager storage
  set {
    name  = "alertmanager.alertmanagerSpec.storage.volumeClaimTemplate.spec.resources.requests.storage"
    value = "2Gi"
  }

  # ---------------------------------------------------------------------------
  # Node Exporter (resource-constrained)
  # ---------------------------------------------------------------------------
  set {
    name  = "nodeExporter.enabled"
    value = "true"
  }

  set {
    name  = "prometheus-node-exporter.resources.requests.cpu"
    value = "25m"
  }

  set {
    name  = "prometheus-node-exporter.resources.requests.memory"
    value = "32Mi"
  }

  set {
    name  = "prometheus-node-exporter.resources.limits.cpu"
    value = "100m"
  }

  set {
    name  = "prometheus-node-exporter.resources.limits.memory"
    value = "64Mi"
  }

  # ---------------------------------------------------------------------------
  # kube-state-metrics (resource-constrained)
  # ---------------------------------------------------------------------------
  set {
    name  = "kube-state-metrics.resources.requests.cpu"
    value = "25m"
  }

  set {
    name  = "kube-state-metrics.resources.requests.memory"
    value = "32Mi"
  }

  set {
    name  = "kube-state-metrics.resources.limits.cpu"
    value = "100m"
  }

  set {
    name  = "kube-state-metrics.resources.limits.memory"
    value = "128Mi"
  }
}
