# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev Flink Operator
# Deploys the Flink Kubernetes Operator for managing FlinkDeployment CRDs
# -----------------------------------------------------------------------------

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}

# Point to the flink-operator Terraform module
terraform {
  source = "../../../modules/flink-operator"
}

# Namespaces must be created before Flink can be deployed
dependency "namespaces" {
  config_path = "../namespaces"

  mock_outputs = {
    namespace_names = ["streamflow-processing"]
  }
}

# Input variables for the flink-operator module
# Resource limits from DESIGN doc
inputs = {
  namespace = "streamflow-processing"

  # Flink Operator resources
  flink_operator_chart_version = "1.10.0"
  operator_memory_request      = "128Mi"
  operator_memory_limit        = "256Mi"
  operator_cpu_request         = "100m"
  operator_cpu_limit           = "200m"

  # Default JobManager resources (can be overridden per FlinkDeployment)
  jobmanager_memory_request = "256Mi"
  jobmanager_memory_limit   = "512Mi"
  jobmanager_cpu_request    = "100m"
  jobmanager_cpu_limit      = "300m"

  # Default TaskManager resources (can be overridden per FlinkDeployment)
  taskmanager_memory_request = "512Mi"
  taskmanager_memory_limit   = "768Mi"
  taskmanager_cpu_request    = "200m"
  taskmanager_cpu_limit      = "500m"
  taskmanager_task_slots     = 2
}
