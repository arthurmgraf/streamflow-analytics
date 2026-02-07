---
# ---------------------------------------------------------------------------
# CloudNativePG Cluster - PostgreSQL 16
# Managed by Terraform for StreamFlow Analytics
# ---------------------------------------------------------------------------
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: ${name}
  namespace: ${namespace}
  labels:
    app.kubernetes.io/part-of: streamflow-analytics
    app.kubernetes.io/managed-by: terraform
    app.kubernetes.io/component: database
spec:
  description: "StreamFlow Analytics PostgreSQL cluster"
  imageName: ghcr.io/cloudnative-pg/postgresql:16

  instances: ${instances}

  postgresql:
    parameters:
      # Memory tuning (conservative for K3s)
      shared_buffers: "64MB"
      effective_cache_size: "128MB"
      work_mem: "4MB"
      maintenance_work_mem: "32MB"

      # WAL configuration
      wal_level: "replica"
      max_wal_senders: "3"

      # Logging
      log_statement: "ddl"
      log_min_duration_statement: "1000"

      # Connection limits
      max_connections: "50"

  bootstrap:
    initdb:
      database: ${database}
      owner: ${owner}
      encoding: "UTF8"
      localeCType: "C"
      localeCollate: "C"

  storage:
    size: ${storage_size}
    storageClass: ""

  resources:
    requests:
      memory: "${memory_request}"
      cpu: "${cpu_request}"
    limits:
      memory: "${memory_limit}"
      cpu: "${cpu_limit}"

  monitoring:
    enablePodMonitor: false

  backup:
    retentionPolicy: "7d"

  nodeMaintenanceWindow:
    inProgress: false
    reusePVC: true
