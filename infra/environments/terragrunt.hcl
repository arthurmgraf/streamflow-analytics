# -----------------------------------------------------------------------------
# StreamFlow Analytics - Root Terragrunt Configuration
# Generates provider.tf for all child modules
# -----------------------------------------------------------------------------

locals {
  env = basename(get_terragrunt_dir())
}

generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<-EOF
    terraform {
      required_version = ">= 1.7"
      required_providers {
        kubernetes = {
          source  = "hashicorp/kubernetes"
          version = "~> 2.35"
        }
        helm = {
          source  = "hashicorp/helm"
          version = "~> 2.17"
        }
        kubectl = {
          source  = "alekc/kubectl"
          version = "~> 2.1"
        }
      }
    }

    provider "kubernetes" {
      config_path = "~/.kube/config"
    }

    provider "helm" {
      kubernetes {
        config_path = "~/.kube/config"
      }
    }

    provider "kubectl" {
      config_path = "~/.kube/config"
    }
  EOF
}
