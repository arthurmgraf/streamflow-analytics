# Knowledge Base

> Curated domain knowledge for AI-grounded development

---

## Overview

The Knowledge Base (KB) provides structured, validated domain knowledge that agents use during the AgentSpec workflow. Each domain contains concepts, patterns, and quick references organized for efficient retrieval.

---

## Structure

```text
.claude/kb/
├── _index.yaml              # Domain registry (machine-readable)
├── _templates/               # Templates for creating new domains
│   ├── concept.md.template
│   ├── pattern.md.template
│   ├── index.md.template
│   ├── quick-reference.md.template
│   ├── spec.yaml.template
│   ├── test-case.json.template
│   └── domain-manifest.yaml.template
│
└── {domain}/                 # One folder per technology domain
    ├── index.md              # Domain overview and navigation
    ├── quick-reference.md    # Cheat sheet for fast lookup
    ├── concepts/             # Atomic concept definitions
    │   └── {concept}.md
    ├── patterns/             # Reusable implementation patterns
    │   └── {pattern}.md
    └── specs/                # Machine-readable specifications (optional)
        └── {spec}.yaml
```

---

## Creating a New Domain

### Option 1: Use the `/create-kb` Command (Recommended)

```bash
/create-kb "React"
```

The `kb-architect` agent will:
1. Research the technology via MCP tools
2. Create the domain structure
3. Populate concepts and patterns
4. Register in `_index.yaml`

### Option 2: Manual Creation

```bash
# 1. Create the domain structure
mkdir -p .claude/kb/react/{concepts,patterns}

# 2. Copy templates
cp .claude/kb/_templates/index.md.template .claude/kb/react/index.md
cp .claude/kb/_templates/quick-reference.md.template .claude/kb/react/quick-reference.md

# 3. Add concepts and patterns using templates
cp .claude/kb/_templates/concept.md.template .claude/kb/react/concepts/hooks.md
cp .claude/kb/_templates/pattern.md.template .claude/kb/react/patterns/state-management.md

# 4. Register in _index.yaml (add your domain to the domains section)
```

---

## File Size Limits

| File Type | Max Lines | Purpose |
|-----------|-----------|---------|
| `quick-reference.md` | 100 | Fast lookup cheat sheet |
| `concepts/*.md` | 150 | Atomic concept definitions |
| `patterns/*.md` | 200 | Implementation patterns with code |
| `specs/*.yaml` | No limit | Machine-readable specifications |

---

## How Agents Use the KB

1. **Define Phase** - Identifies relevant KB domains in Technical Context
2. **Design Phase** - Reads patterns for architecture decisions
3. **Build Phase** - Agents consult domain patterns for implementation
4. **Any Agent** - Can load KB patterns for domain-specific tasks

```text
DEFINE                    DESIGN                    BUILD
──────                    ──────                    ─────

KB Domains:          →    Read patterns:       →    Agents consult:
• react                   • state-management        • KB/react/patterns/
• typescript              • component-patterns       • KB/typescript/patterns/
```

---

## Best Practices

1. **Keep concepts atomic** - One concept per file, max 150 lines
2. **Make patterns copy-paste ready** - Include working code examples
3. **Use MCP validation** - Verify against official documentation
4. **Update regularly** - Mark stale content, refresh after major versions
5. **Reference in DEFINE** - Always list relevant KB domains in Technical Context
