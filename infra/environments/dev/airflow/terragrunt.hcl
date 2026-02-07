# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev Airflow
# Deploys Apache Airflow via Helm with LocalExecutor (ADR-002)
# -----------------------------------------------------------------------------

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}

# Point to the airflow Terraform module
terraform {
  source = "../../../modules/airflow"
}

# Namespaces must be created before Airflow can be deployed
dependency "namespaces" {
  config_path = "../namespaces"

  mock_outputs = {
    namespace_names = ["streamflow-orchestration"]
  }
}

# PostgreSQL must be running for Airflow metadata database connection
dependency "postgresql" {
  config_path = "../postgresql"

  mock_outputs = {
    pg_host     = "streamflow-pg-rw.streamflow-data.svc.cluster.local"
    pg_port     = 5432
    pg_database = "streamflow"
  }
}

# Input variables for the airflow module
# Resource limits from DESIGN doc (ADR-002: LocalExecutor)
inputs = {
  namespace = "streamflow-orchestration"

  # Airflow Helm chart configuration
  airflow_chart_version = "1.15.0"
  executor              = "LocalExecutor"

  # Webserver resources
  webserver_memory_request = "256Mi"
  webserver_memory_limit   = "384Mi"
  webserver_cpu_request    = "100m"
  webserver_cpu_limit      = "200m"

  # Scheduler resources (also executes tasks in LocalExecutor mode)
  scheduler_memory_request = "256Mi"
  scheduler_memory_limit   = "384Mi"
  scheduler_cpu_request    = "100m"
  scheduler_cpu_limit      = "200m"

  # PostgreSQL connection for Airflow metadata
  pg_host     = dependency.postgresql.outputs.pg_host
  pg_port     = dependency.postgresql.outputs.pg_port
  pg_database = dependency.postgresql.outputs.pg_database
}
