# -----------------------------------------------------------------------------
# StreamFlow Analytics - CloudNativePG Module Outputs
# -----------------------------------------------------------------------------

output "pg_rw_service" {
  description = "PostgreSQL read-write service endpoint for application connections"
  value       = "${var.pg_cluster_name}-rw.${var.namespace}.svc.cluster.local"
}

output "pg_database" {
  description = "Name of the application database"
  value       = var.pg_database
}

output "pg_owner" {
  description = "Database owner role name"
  value       = var.pg_owner
}
