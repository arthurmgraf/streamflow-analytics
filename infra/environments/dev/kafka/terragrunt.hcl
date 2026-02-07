# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev Kafka (Strimzi)
# Deploys Strimzi operator and single-node KRaft Kafka cluster
# -----------------------------------------------------------------------------

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}

# Point to the strimzi-kafka Terraform module
terraform {
  source = "../../../modules/strimzi-kafka"
}

# Namespaces must be created before Kafka can be deployed
dependency "namespaces" {
  config_path = "../namespaces"

  mock_outputs = {
    namespace_names = ["streamflow-kafka"]
  }
}

# Input variables for the strimzi-kafka module
# Resource limits from DESIGN doc (single-node K3s, 4GB budget)
inputs = {
  namespace = "streamflow-kafka"

  # Strimzi Operator resources
  strimzi_chart_version    = "0.44.0"
  operator_memory_request  = "128Mi"
  operator_memory_limit    = "256Mi"
  operator_cpu_request     = "100m"
  operator_cpu_limit       = "200m"

  # Kafka Broker resources (KRaft, single node)
  kafka_cluster_name  = "streamflow"
  kafka_replicas      = 1
  kafka_storage_size  = "10Gi"
  kafka_memory_request = "512Mi"
  kafka_memory_limit   = "768Mi"
  kafka_cpu_request    = "200m"
  kafka_cpu_limit      = "500m"
}
