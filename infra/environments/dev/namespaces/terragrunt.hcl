# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev Namespaces
# Creates all Kubernetes namespaces for the StreamFlow platform
# -----------------------------------------------------------------------------

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}

# Point to the namespaces Terraform module
terraform {
  source = "../../../modules/namespaces"
}

# Input variables for the namespaces module
inputs = {
  namespaces = [
    "streamflow-kafka",
    "streamflow-processing",
    "streamflow-data",
    "streamflow-orchestration",
    "streamflow-monitoring",
  ]
}
