# -----------------------------------------------------------------------------
# StreamFlow Analytics - Flink Operator Module Variables
# -----------------------------------------------------------------------------

variable "namespace" {
  description = "Kubernetes namespace for the Flink operator deployment"
  type        = string
}

variable "chart_version" {
  description = "Flink Kubernetes Operator Helm chart version"
  type        = string
  default     = "1.10.0"
}
