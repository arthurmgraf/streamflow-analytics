# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev Monitoring
# Deploys kube-prometheus-stack (Prometheus + Grafana + AlertManager)
# -----------------------------------------------------------------------------

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}

# Point to the monitoring Terraform module
terraform {
  source = "../../../modules/monitoring"
}

# Namespaces must be created before monitoring can be deployed
dependency "namespaces" {
  config_path = "../namespaces"

  mock_outputs = {
    namespace_names = ["streamflow-monitoring"]
  }
}

# Input variables for the monitoring module
# Resource limits from DESIGN doc
inputs = {
  namespace = "streamflow-monitoring"

  # kube-prometheus-stack Helm chart
  prometheus_stack_chart_version = "65.1.0"

  # Prometheus resources
  prometheus_memory_request = "256Mi"
  prometheus_memory_limit   = "384Mi"
  prometheus_cpu_request    = "100m"
  prometheus_cpu_limit      = "200m"
  prometheus_retention      = "7d"
  prometheus_storage_size   = "10Gi"

  # Grafana resources
  grafana_memory_request = "128Mi"
  grafana_memory_limit   = "192Mi"
  grafana_cpu_request    = "50m"
  grafana_cpu_limit      = "100m"
  grafana_admin_password = "admin"  # Dev only; override in prod

  # AlertManager (lightweight, using stack defaults)
  alertmanager_enabled = true
}
