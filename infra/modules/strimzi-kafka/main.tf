# -----------------------------------------------------------------------------
# StreamFlow Analytics - Strimzi Kafka Module
# Deploys Strimzi operator via Helm and creates Kafka cluster + topics via CRDs
# Uses KRaft mode (no ZooKeeper dependency)
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
  }
}

# ---------------------------------------------------------------------------
# Strimzi Kafka Operator (Helm)
# ---------------------------------------------------------------------------
resource "helm_release" "strimzi_operator" {
  name             = "strimzi-kafka-operator"
  repository       = "https://strimzi.io/charts/"
  chart            = "strimzi-kafka-operator"
  version          = var.strimzi_chart_version
  namespace        = var.namespace
  create_namespace = false

  set {
    name  = "watchAnyNamespace"
    value = "false"
  }

  set {
    name  = "watchNamespaces"
    value = "{${var.namespace}}"
  }
}

# ---------------------------------------------------------------------------
# Kafka Cluster CRD (KRaft mode - no ZooKeeper)
# ---------------------------------------------------------------------------
resource "kubectl_manifest" "kafka_node_pool" {
  yaml_body = templatefile(
    "${path.module}/templates/kafka-cluster.yaml.tpl",
    {
      name           = var.kafka_cluster_name
      namespace      = var.namespace
      replicas       = var.kafka_replicas
      storage_size   = var.kafka_storage_size
      memory_request = var.kafka_memory_request
      memory_limit   = var.kafka_memory_limit
      cpu_request    = var.kafka_cpu_request
      cpu_limit      = var.kafka_cpu_limit
    }
  )

  depends_on = [helm_release.strimzi_operator]
}

# ---------------------------------------------------------------------------
# Kafka Topics
# ---------------------------------------------------------------------------
resource "kubectl_manifest" "topic_transactions_raw" {
  yaml_body = <<-YAML
    apiVersion: kafka.strimzi.io/v1beta2
    kind: KafkaTopic
    metadata:
      name: transactions.raw
      namespace: ${var.namespace}
      labels:
        strimzi.io/cluster: ${var.kafka_cluster_name}
        app.kubernetes.io/part-of: streamflow-analytics
    spec:
      partitions: 3
      replicas: ${min(var.kafka_replicas, 3)}
      config:
        retention.ms: "604800000"
        cleanup.policy: "delete"
        min.insync.replicas: "1"
  YAML

  depends_on = [kubectl_manifest.kafka_node_pool]
}

resource "kubectl_manifest" "topic_fraud_alerts" {
  yaml_body = <<-YAML
    apiVersion: kafka.strimzi.io/v1beta2
    kind: KafkaTopic
    metadata:
      name: fraud.alerts
      namespace: ${var.namespace}
      labels:
        strimzi.io/cluster: ${var.kafka_cluster_name}
        app.kubernetes.io/part-of: streamflow-analytics
    spec:
      partitions: 1
      replicas: ${min(var.kafka_replicas, 3)}
      config:
        retention.ms: "2592000000"
        cleanup.policy: "delete"
        min.insync.replicas: "1"
  YAML

  depends_on = [kubectl_manifest.kafka_node_pool]
}

resource "kubectl_manifest" "topic_metrics_realtime" {
  yaml_body = <<-YAML
    apiVersion: kafka.strimzi.io/v1beta2
    kind: KafkaTopic
    metadata:
      name: metrics.realtime
      namespace: ${var.namespace}
      labels:
        strimzi.io/cluster: ${var.kafka_cluster_name}
        app.kubernetes.io/part-of: streamflow-analytics
    spec:
      partitions: 1
      replicas: ${min(var.kafka_replicas, 3)}
      config:
        retention.ms: "86400000"
        cleanup.policy: "delete"
        min.insync.replicas: "1"
  YAML

  depends_on = [kubectl_manifest.kafka_node_pool]
}
