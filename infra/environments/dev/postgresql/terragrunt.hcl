# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev PostgreSQL (CloudNativePG)
# Deploys CNPG operator and single-instance PostgreSQL 16 cluster
# -----------------------------------------------------------------------------

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}

# Point to the cloudnativepg Terraform module
terraform {
  source = "../../../modules/cloudnativepg"
}

# Namespaces must be created before PostgreSQL can be deployed
dependency "namespaces" {
  config_path = "../namespaces"

  mock_outputs = {
    namespace_names = ["streamflow-data"]
  }
}

# Input variables for the cloudnativepg module
# Resource limits from DESIGN doc (ADR-003: single instance, no replica)
inputs = {
  namespace = "streamflow-data"

  # CNPG Operator resources
  cnpg_chart_version       = "0.23.0"
  operator_memory_request  = "64Mi"
  operator_memory_limit    = "128Mi"
  operator_cpu_request     = "50m"
  operator_cpu_limit       = "100m"

  # PostgreSQL Cluster configuration
  pg_cluster_name = "streamflow-pg"
  pg_version      = 16
  pg_instances    = 1  # ADR-003: single instance, no replica
  pg_storage_size = "10Gi"
  pg_database     = "streamflow"
  pg_owner        = "streamflow"

  # PostgreSQL instance resources
  pg_memory_request = "256Mi"
  pg_memory_limit   = "512Mi"
  pg_cpu_request    = "200m"
  pg_cpu_limit      = "500m"
}
