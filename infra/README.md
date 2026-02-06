# Infrastructure as Code

> Infrastructure provisioning and management

---

## Structure

```text
infra/
├── README.md              # This file
│
├── modules/               # Reusable infrastructure modules
│   └── {{module_name}}/   # One folder per module
│       ├── main.tf        # Resource definitions
│       ├── variables.tf   # Input variables
│       ├── outputs.tf     # Output values
│       └── README.md      # Module documentation
│
├── environments/          # Environment-specific configurations
│   ├── dev/               # Development environment
│   │   └── .gitkeep
│   └── prod/              # Production environment
│       └── .gitkeep
│
└── scripts/               # Infrastructure helper scripts
    └── .gitkeep           # e.g., init.sh, plan.sh, apply.sh
```

---

## Modules

Create reusable modules for each infrastructure component:

| Module | Purpose | Example Resources |
|--------|---------|-------------------|
| `compute` | Compute resources | VMs, containers, serverless |
| `storage` | Storage resources | Buckets, databases, caches |
| `networking` | Network configuration | VPCs, subnets, firewalls |
| `iam` | Identity and access | Service accounts, roles |
| `messaging` | Event messaging | Topics, subscriptions, queues |
| `secrets` | Secret management | API keys, credentials |

---

## Environments

Each environment folder contains environment-specific overrides:

```text
environments/
├── dev/
│   ├── terragrunt.hcl     # or terraform.tfvars
│   ├── compute/
│   ├── storage/
│   └── ...
│
└── prod/
    ├── terragrunt.hcl     # or terraform.tfvars
    ├── compute/
    ├── storage/
    └── ...
```

---

## Usage

### With Terraform

```bash
cd infra/environments/dev
terraform init
terraform plan
terraform apply
```

### With Terragrunt

```bash
cd infra/environments/dev
terragrunt run-all plan
terragrunt run-all apply
```

---

## Best Practices

1. **Module per resource type** - Keep modules focused and reusable
2. **Environment isolation** - Separate state per environment
3. **Least privilege** - IAM roles with minimum required permissions
4. **Secret management** - Never commit secrets, use Secret Manager
5. **Remote state** - Store state in cloud storage with locking
6. **Version pinning** - Pin provider and module versions
