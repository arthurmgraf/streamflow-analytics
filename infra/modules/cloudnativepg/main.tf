# -----------------------------------------------------------------------------
# StreamFlow Analytics - CloudNativePG Module
# Deploys the CloudNativePG operator via Helm and creates a PostgreSQL cluster
# with Medallion architecture schemas (bronze, silver, gold)
# -----------------------------------------------------------------------------

terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">= 2.12.0"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.14.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.25.0"
    }
  }
}

# ---------------------------------------------------------------------------
# CloudNativePG Operator (Helm)
# ---------------------------------------------------------------------------
resource "helm_release" "cnpg_operator" {
  name             = "cloudnative-pg"
  repository       = "https://cloudnative-pg.github.io/charts"
  chart            = "cloudnative-pg"
  version          = var.cnpg_chart_version
  namespace        = var.namespace
  create_namespace = false

  set {
    name  = "resources.requests.memory"
    value = "128Mi"
  }

  set {
    name  = "resources.requests.cpu"
    value = "100m"
  }

  set {
    name  = "resources.limits.memory"
    value = "256Mi"
  }

  set {
    name  = "resources.limits.cpu"
    value = "200m"
  }
}

# ---------------------------------------------------------------------------
# PostgreSQL Cluster CRD
# ---------------------------------------------------------------------------
resource "kubectl_manifest" "pg_cluster" {
  yaml_body = templatefile(
    "${path.module}/templates/pg-cluster.yaml.tpl",
    {
      name           = var.pg_cluster_name
      namespace      = var.namespace
      instances      = var.pg_instances
      storage_size   = var.pg_storage_size
      memory_request = var.pg_memory_request
      memory_limit   = var.pg_memory_limit
      cpu_request    = var.pg_cpu_request
      cpu_limit      = var.pg_cpu_limit
      database       = var.pg_database
      owner          = var.pg_owner
    }
  )

  depends_on = [helm_release.cnpg_operator]
}

# ---------------------------------------------------------------------------
# Medallion Architecture Schemas (bronze, silver, gold)
# Created via a Kubernetes Job that runs psql after the cluster is ready
# ---------------------------------------------------------------------------
resource "kubernetes_config_map" "schema_init" {
  metadata {
    name      = "${var.pg_cluster_name}-schema-init"
    namespace = var.namespace

    labels = {
      "app.kubernetes.io/part-of"    = "streamflow-analytics"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  data = {
    "init-schemas.sql" = <<-SQL
      -- Medallion architecture schemas for StreamFlow Analytics
      CREATE SCHEMA IF NOT EXISTS bronze;
      COMMENT ON SCHEMA bronze IS 'Raw ingestion layer - unprocessed data from sources';

      CREATE SCHEMA IF NOT EXISTS silver;
      COMMENT ON SCHEMA silver IS 'Cleansed and enriched data - validated and deduplicated';

      CREATE SCHEMA IF NOT EXISTS gold;
      COMMENT ON SCHEMA gold IS 'Business-level aggregates - ready for consumption';

      -- Grant usage to the database owner
      GRANT ALL PRIVILEGES ON SCHEMA bronze TO ${var.pg_owner};
      GRANT ALL PRIVILEGES ON SCHEMA silver TO ${var.pg_owner};
      GRANT ALL PRIVILEGES ON SCHEMA gold TO ${var.pg_owner};
    SQL
  }

  depends_on = [kubectl_manifest.pg_cluster]
}

resource "kubernetes_job" "schema_init" {
  metadata {
    name      = "${var.pg_cluster_name}-schema-init"
    namespace = var.namespace

    labels = {
      "app.kubernetes.io/part-of"    = "streamflow-analytics"
      "app.kubernetes.io/managed-by" = "terraform"
    }
  }

  spec {
    backoff_limit = 3

    template {
      metadata {
        labels = {
          "app.kubernetes.io/part-of"    = "streamflow-analytics"
          "app.kubernetes.io/component"  = "schema-init"
        }
      }

      spec {
        restart_policy = "OnFailure"

        container {
          name    = "schema-init"
          image   = "postgres:16-alpine"
          command = ["psql", "-f", "/scripts/init-schemas.sql"]

          env {
            name  = "PGHOST"
            value = "${var.pg_cluster_name}-rw.${var.namespace}.svc.cluster.local"
          }

          env {
            name  = "PGDATABASE"
            value = var.pg_database
          }

          env {
            name = "PGUSER"
            value_from {
              secret_key_ref {
                name = "${var.pg_cluster_name}-superuser"
                key  = "username"
              }
            }
          }

          env {
            name = "PGPASSWORD"
            value_from {
              secret_key_ref {
                name = "${var.pg_cluster_name}-superuser"
                key  = "password"
              }
            }
          }

          volume_mount {
            name       = "scripts"
            mount_path = "/scripts"
            read_only  = true
          }

          resources {
            requests = {
              cpu    = "50m"
              memory = "64Mi"
            }
            limits = {
              cpu    = "100m"
              memory = "128Mi"
            }
          }
        }

        volume {
          name = "scripts"

          config_map {
            name = kubernetes_config_map.schema_init.metadata[0].name
          }
        }
      }
    }
  }

  wait_for_completion = true

  timeouts {
    create = "5m"
  }

  depends_on = [kubectl_manifest.pg_cluster]
}
