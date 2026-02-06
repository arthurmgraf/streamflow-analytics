# AgentSpec Examples

> Place real-world example artifacts here to guide future feature development

---

## Purpose

This folder stores completed examples of the AgentSpec workflow to serve as reference material. Each example should demonstrate the full pipeline:

```text
BRAINSTORM_*.md → DEFINE_*.md → DESIGN_*.md → BUILD_REPORT_*.md
```

---

## How to Add Examples

After shipping your first feature with `/ship`, copy the archived artifacts here:

```bash
cp .claude/sdd/archive/{FEATURE}/* .claude/sdd/examples/
```

---

## Key Patterns to Demonstrate

| Phase | What to Show |
|-------|-------------|
| **Brainstorm** | Discovery questions, approaches explored, YAGNI applied |
| **Define** | Problem statement, Technical Context, success criteria |
| **Design** | Architecture diagram, file manifest with Agent column |
| **Build Report** | Task execution, agent attribution, verification results |

---

## Note

Examples should be project-specific to your domain. The structure and patterns are universal, but the content should reflect your actual technology stack and architecture decisions.
