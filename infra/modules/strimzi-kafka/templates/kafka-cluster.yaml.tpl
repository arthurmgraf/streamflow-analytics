---
# ---------------------------------------------------------------------------
# Strimzi KafkaNodePool - Broker pool definition (KRaft mode)
# ---------------------------------------------------------------------------
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaNodePool
metadata:
  name: ${name}-broker
  namespace: ${namespace}
  labels:
    strimzi.io/cluster: ${name}
    app.kubernetes.io/part-of: streamflow-analytics
    app.kubernetes.io/managed-by: terraform
spec:
  replicas: ${replicas}
  roles:
    - controller
    - broker
  storage:
    type: persistent-claim
    size: ${storage_size}
    deleteClaim: false
  resources:
    requests:
      memory: "${memory_request}"
      cpu: "${cpu_request}"
    limits:
      memory: "${memory_limit}"
      cpu: "${cpu_limit}"
---
# ---------------------------------------------------------------------------
# Strimzi Kafka Cluster - KRaft mode (no ZooKeeper)
# ---------------------------------------------------------------------------
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: ${name}
  namespace: ${namespace}
  labels:
    app.kubernetes.io/part-of: streamflow-analytics
    app.kubernetes.io/managed-by: terraform
  annotations:
    strimzi.io/kraft: "enabled"
    strimzi.io/node-pools: "enabled"
spec:
  kafka:
    version: "3.8.0"
    metadataVersion: "3.8-IV0"
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: ${replicas}
      transaction.state.log.replication.factor: ${replicas}
      transaction.state.log.min.isr: 1
      default.replication.factor: ${replicas}
      min.insync.replicas: 1
      log.message.format.version: "3.8"
      inter.broker.protocol.version: "3.8"
      auto.create.topics.enable: "false"
      log.retention.hours: 168
    readinessProbe:
      initialDelaySeconds: 15
      timeoutSeconds: 5
    livenessProbe:
      initialDelaySeconds: 15
      timeoutSeconds: 5
  entityOperator:
    topicOperator: {}
    userOperator: {}
