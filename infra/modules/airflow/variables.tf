# -----------------------------------------------------------------------------
# StreamFlow Analytics - Airflow Module Variables
# -----------------------------------------------------------------------------

variable "namespace" {
  description = "Kubernetes namespace for the Airflow deployment"
  type        = string
}

variable "chart_version" {
  description = "Apache Airflow official Helm chart version"
  type        = string
  default     = "1.15.0"
}

variable "executor" {
  description = "Airflow executor type (LocalExecutor for single-node, CeleryExecutor for distributed)"
  type        = string
  default     = "LocalExecutor"

  validation {
    condition     = contains(["LocalExecutor", "CeleryExecutor", "KubernetesExecutor"], var.executor)
    error_message = "Executor must be one of: LocalExecutor, CeleryExecutor, KubernetesExecutor."
  }
}

variable "webserver_replicas" {
  description = "Number of Airflow webserver replicas"
  type        = number
  default     = 1

  validation {
    condition     = var.webserver_replicas >= 1
    error_message = "Webserver replicas must be at least 1."
  }
}
