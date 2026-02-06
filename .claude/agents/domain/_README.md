# Domain Agents

> Project-specific specialized agents

---

## Overview

This folder contains agents specific to YOUR project. Unlike the universal agents in other categories, domain agents are tailored to your particular technology stack, architecture, and business domain.

---

## When to Create Domain Agents

Create a domain agent when:

- A specific role is needed repeatedly across features
- The agent needs deep knowledge of your project's patterns
- Standard agents don't cover your project's specialized needs

---

## How to Create a Domain Agent

1. Copy the template:

```bash
cp .claude/agents/_template.md.example .claude/agents/domain/my-specialist.md
```

2. Customize the agent's identity, capabilities, and knowledge sources

3. The agent becomes automatically discoverable by the Design phase via `Glob(.claude/agents/**/*.md)`

---

## Examples

Here are examples of domain agents for different project types:

### Backend Project

```
api-specialist.md          - REST/GraphQL API design and implementation
database-specialist.md     - Schema design, migrations, query optimization
auth-specialist.md         - Authentication and authorization patterns
```

### Frontend Project

```
component-specialist.md    - UI component architecture
state-specialist.md        - State management patterns
accessibility-specialist.md - WCAG compliance and a11y
```

### Data Project

```
pipeline-specialist.md     - ETL/ELT pipeline architecture
extraction-specialist.md   - Data extraction and parsing
warehouse-specialist.md    - Data warehouse modeling
```

### Mobile Project

```
navigation-specialist.md   - App navigation architecture
offline-specialist.md      - Offline-first data synchronization
platform-specialist.md     - Platform-specific implementations
```

---

## Naming Convention

Use kebab-case with a descriptive role suffix:

```
{role}-specialist.md
{role}-architect.md
{role}-developer.md
{role}-builder.md
```

---

## Tips

- **Use specific keywords** in the agent description for better matching during Design phase
- **Reference KB domains** the agent should consult
- **Define clear capabilities** so the Design phase can match files to agents accurately
- **Keep agents focused** - one role per agent, not a generalist
