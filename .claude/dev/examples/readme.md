# Dev Loop Examples

> Place real-world example artifacts here to demonstrate the Dev Loop workflow

---

## Purpose

This folder stores completed examples of the Dev Loop workflow. Each example should include:

| File | Type | Description |
|------|------|-------------|
| `PROMPT_*.md` | PROMPT | Task definition with prioritized checklist |
| `PROGRESS_*.md` | PROGRESS | Memory bridge showing iteration history |
| `LOG_*.md` | LOG | Final execution report with statistics |

---

## How to Add Examples

After completing a Dev Loop session, copy the artifacts here:

```bash
cp .claude/dev/tasks/PROMPT_MY_FEATURE.md .claude/dev/examples/
cp .claude/dev/progress/PROGRESS_MY_FEATURE.md .claude/dev/examples/
cp .claude/dev/logs/LOG_MY_FEATURE_*.md .claude/dev/examples/
```

---

## Key Patterns to Demonstrate

- **Task prioritization** with RISKY/CORE/POLISH system
- **Agent references** (`@agent-name`) for specialist delegation
- **Exit criteria** with objective verification commands
- **Memory bridge** progress tracking across sessions
- **Session recovery** using `--resume`

---

## Templates

For creating your own PROMPTs, see:

- `templates/PROMPT_TEMPLATE.md` - Blank template with all sections
- `templates/PROMPT_EXAMPLE_FEATURE.md` - Simple Python utility example
- `templates/PROMPT_EXAMPLE_KB.md` - Knowledge base building example
