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

- All secrets managed via Kubernetes Secrets (no hardcoded values)
- Infrastructure deployed via Terraform with state encryption
- Kafka TLS encryption for inter-broker communication
- PostgreSQL connections with SSL required
- CI/CD with secret scanning enabled
