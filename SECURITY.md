# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue
2. Email: arthurmgraf@hotmail.com
3. Include a detailed description of the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Security Practices

### Implemented

- All secrets managed via environment variables / K8s Secrets (zero hardcoded passwords in repo)
- Infrastructure deployed via Terraform with state locking
- Flink pods: `runAsNonRoot`, `drop ALL` capabilities, `readOnlyRootFilesystem: true` with emptyDir volumes
- NetworkPolicies with default-deny ingress per namespace, explicit allow-lists
- PodDisruptionBudgets on all stateful workloads (Kafka, PostgreSQL, Flink)
- `pip-audit --strict` in CI for dependency vulnerability scanning
- Pydantic validation at ingestion boundary (prevents injection via data layer)
- `yaml.safe_load` for all YAML parsing (prevents arbitrary code execution)
- `json.loads` / `json.dumps` for all serialization (no pickle in application code)
- RBAC least-privilege: dedicated Flink ServiceAccount with minimal Role (ConfigMap read-only)
- SQL parameterized queries (`%s` psycopg2, `?` JDBC) — zero string interpolation
- Migration checksum tamper detection (SHA256 verification of applied migrations)
- ML model SHA256 checksum validation before `joblib.load()`
- All SQL queries use `ON CONFLICT DO NOTHING` for idempotent processing
- Structured JSON logging with PII protection (no emails, passwords, card numbers logged)
- Log injection prevention: raw event truncation to 200 chars in logs, 10KB in DLQ
- GitHub Actions: `permissions: contents: read` (minimal), `pip-audit`, `kubeval`
- Docker: all containers run as non-root (flink:9999, generator:nobody, airflow:airflow)
- `mypy --strict` enforces type safety across 36 source files (zero errors)
- `.gitignore` covers `.env*`, `*.pem`, `*.key`, `credentials.json`, `terraform.tfstate`

### Planned Improvements

- Kafka TLS encryption for inter-broker and client communication (Strimzi listener `tls: true`)
- PostgreSQL SSL (`sslmode=verify-full`) with certificate rotation
- Secret rotation via External Secrets Operator
