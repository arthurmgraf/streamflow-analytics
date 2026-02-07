# -----------------------------------------------------------------------------
# StreamFlow Analytics - Strimzi Kafka Module Outputs
# -----------------------------------------------------------------------------

output "bootstrap_servers" {
  description = "Kafka bootstrap servers endpoint for internal cluster communication"
  value       = "${var.kafka_cluster_name}-kafka-bootstrap.${var.namespace}.svc.cluster.local:9092"
}

output "kafka_cluster_name" {
  description = "Name of the deployed Kafka cluster"
  value       = var.kafka_cluster_name
}
