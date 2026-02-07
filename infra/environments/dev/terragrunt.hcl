# -----------------------------------------------------------------------------
# StreamFlow Analytics - Dev Environment Base Configuration
# All child modules in dev/ inherit this configuration
# -----------------------------------------------------------------------------

locals {
  environment = "dev"

  # Common tags applied to all resources in this environment
  common_tags = {
    environment = local.environment
    project     = "streamflow-analytics"
    managed_by  = "terragrunt"
  }
}

# Include root terragrunt.hcl for provider generation
include "root" {
  path = find_in_parent_folders()
}
