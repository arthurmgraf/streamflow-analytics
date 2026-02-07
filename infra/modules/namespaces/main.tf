# -----------------------------------------------------------------------------
# StreamFlow Analytics - Kubernetes Namespaces
# Creates isolated namespaces for each platform component
# -----------------------------------------------------------------------------

terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.25.0"
    }
  }
}

resource "kubernetes_namespace" "streamflow" {
  for_each = toset(var.namespaces)

  metadata {
    name = each.value

    labels = {
      "app.kubernetes.io/part-of"    = "streamflow-analytics"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }
}
