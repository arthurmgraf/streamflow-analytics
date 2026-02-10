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

- All secrets managed via Kubernetes Secrets (no hardcoded values)
- Infrastructure deployed via Terraform with state locking
- Flink pods: `runAsNonRoot`, `drop ALL` capabilities, `readOnlyRootFilesystem`
- NetworkPolicies with default-deny ingress/egress per namespace
- PodDisruptionBudgets on all stateful workloads
- `pip-audit` in CI for dependency vulnerability scanning
- Pydantic validation at ingestion boundary (prevents injection via data layer)
- `yaml.safe_load` for all YAML parsing (prevents arbitrary code execution)

### Planned Improvements

- Kafka TLS encryption for inter-broker and client communication (Strimzi listener `tls: true`)
- PostgreSQL SSL (`sslmode=verify-full`) with certificate rotation
- Secret rotation via External Secrets Operator
- RBAC least-privilege for K8s service accounts
