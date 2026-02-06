---
name: commit
description: Creates well-structured git commits following conventional commit format. Use when committing code changes.
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# Commit Commands

Create well-structured git commits following Conventional Commits format.

## Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting, no logic change |
| `refactor` | Code restructuring, no behavior change |
| `perf` | Performance improvement |
| `test` | Adding or updating tests |
| `build` | Build system or dependencies |
| `ci` | CI/CD configuration |
| `chore` | Maintenance tasks |

### Scope

Use the module, component, or area affected:
- `auth`, `api`, `db`, `ui`, `config`, `infra`, etc.

## Process

1. Run `git status` to see all changes
2. Run `git diff --staged` to review staged changes
3. Run `git log --oneline -5` to match existing commit style
4. Analyze the nature of changes (feat, fix, refactor, etc.)
5. Draft a concise commit message focusing on "why" not "what"
6. Stage relevant files (avoid `git add .` -- be explicit)
7. Create the commit

## Rules

- Keep subject line under 72 characters
- Use imperative mood ("add feature" not "added feature")
- Do NOT commit `.env`, credentials, or secret files
- Do NOT use `--no-verify` unless explicitly asked
- Do NOT amend previous commits unless explicitly asked
- Always create NEW commits (never amend by default)

## Usage

```bash
# Commit staged changes
/commit

# Commit with a hint about the change
/commit "added user validation"
```