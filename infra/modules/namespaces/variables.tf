# -----------------------------------------------------------------------------
# StreamFlow Analytics - Namespaces Module Variables
# -----------------------------------------------------------------------------

variable "namespaces" {
  description = "List of Kubernetes namespaces to create for the StreamFlow platform"
  type        = list(string)
  default = [
    "streamflow-kafka",
    "streamflow-processing",
    "streamflow-data",
    "streamflow-orchestration",
    "streamflow-monitoring",
  ]
}
