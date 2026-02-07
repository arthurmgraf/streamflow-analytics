# -----------------------------------------------------------------------------
# StreamFlow Analytics - Strimzi Kafka Module Variables
# -----------------------------------------------------------------------------

variable "namespace" {
  description = "Kubernetes namespace for the Kafka cluster and operator"
  type        = string
}

variable "strimzi_chart_version" {
  description = "Strimzi Kafka operator Helm chart version"
  type        = string
  default     = "0.44.0"
}

variable "kafka_cluster_name" {
  description = "Name of the Kafka cluster resource"
  type        = string
  default     = "streamflow"
}

variable "kafka_replicas" {
  description = "Number of Kafka broker replicas"
  type        = number
  default     = 1

  validation {
    condition     = var.kafka_replicas >= 1
    error_message = "Kafka replicas must be at least 1."
  }
}

variable "kafka_storage_size" {
  description = "Persistent volume size for each Kafka broker"
  type        = string
  default     = "10Gi"
}

variable "kafka_memory_request" {
  description = "Memory request for each Kafka broker pod"
  type        = string
  default     = "512Mi"
}

variable "kafka_memory_limit" {
  description = "Memory limit for each Kafka broker pod"
  type        = string
  default     = "768Mi"
}

variable "kafka_cpu_request" {
  description = "CPU request for each Kafka broker pod"
  type        = string
  default     = "200m"
}

variable "kafka_cpu_limit" {
  description = "CPU limit for each Kafka broker pod"
  type        = string
  default     = "500m"
}
