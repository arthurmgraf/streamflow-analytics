# -----------------------------------------------------------------------------
# StreamFlow Analytics - CloudNativePG Module Variables
# -----------------------------------------------------------------------------

variable "namespace" {
  description = "Kubernetes namespace for the PostgreSQL cluster"
  type        = string
}

variable "cnpg_chart_version" {
  description = "CloudNativePG operator Helm chart version"
  type        = string
  default     = "0.23.0"
}

variable "pg_cluster_name" {
  description = "Name of the CloudNativePG cluster resource"
  type        = string
  default     = "streamflow-pg"
}

variable "pg_instances" {
  description = "Number of PostgreSQL instances (1 = standalone, 2+ = HA with streaming replication)"
  type        = number
  default     = 1

  validation {
    condition     = var.pg_instances >= 1
    error_message = "PostgreSQL instances must be at least 1."
  }
}

variable "pg_storage_size" {
  description = "Persistent volume size for each PostgreSQL instance"
  type        = string
  default     = "10Gi"
}

variable "pg_memory_request" {
  description = "Memory request for each PostgreSQL instance pod"
  type        = string
  default     = "256Mi"
}

variable "pg_memory_limit" {
  description = "Memory limit for each PostgreSQL instance pod"
  type        = string
  default     = "512Mi"
}

variable "pg_cpu_request" {
  description = "CPU request for each PostgreSQL instance pod"
  type        = string
  default     = "200m"
}

variable "pg_cpu_limit" {
  description = "CPU limit for each PostgreSQL instance pod"
  type        = string
  default     = "500m"
}

variable "pg_database" {
  description = "Name of the application database to create"
  type        = string
  default     = "streamflow"
}

variable "pg_owner" {
  description = "Database owner role name"
  type        = string
  default     = "streamflow"
}
