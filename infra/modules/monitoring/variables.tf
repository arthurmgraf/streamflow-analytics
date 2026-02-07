# -----------------------------------------------------------------------------
# StreamFlow Analytics - Monitoring Module Variables
# -----------------------------------------------------------------------------

variable "namespace" {
  description = "Kubernetes namespace for the monitoring stack deployment"
  type        = string
}

variable "chart_version" {
  description = "kube-prometheus-stack Helm chart version"
  type        = string
  default     = "67.4.0"
}

variable "grafana_admin_password" {
  description = "Grafana admin user password"
  type        = string
  default     = "admin"
  sensitive   = true
}
