---
name: setup-project
description: Adapt this Claude Code template to a new project by replacing all placeholders and configuring the environment
---

# Setup Project Command

Adapts the Claude Code template to a new project through an interactive questionnaire that replaces all `{{PLACEHOLDERS}}` across configuration files.

## Usage

```bash
/setup-project                    # Full interactive setup
/setup-project --check            # Validate: list remaining placeholders
```

---

## Execution Flow

```text
1. Gather project info (questions)
   │
   ▼
2. Replace placeholders in CLAUDE.md, README.md, pyproject.toml
   │
   ▼
3. Update project structure sections
   │
   ▼
4. Run /sync-context to detect codebase patterns
   │
   ▼
5. Summary report
```

---

## Step 1: Gather Project Information

Ask the user the following questions **interactively** using AskUserQuestion. Group them logically.

### Group 1 — Identity

| Placeholder | Question | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | What is your project name? | `Invoice Pipeline` |
| `{{PROJECT_DESCRIPTION}}` | One-line description? | `AI-powered invoice extraction and processing pipeline` |
| `{{PROJECT_ROOT}}` | Root folder name? | `invoice-pipeline` |

### Group 2 — Business Context

| Placeholder | Question | Example |
|---|---|---|
| `{{BUSINESS_PROBLEM}}` | What business problem does this solve? | `Manual invoice processing is slow and error-prone` |
| `{{SOLUTION_DESCRIPTION}}` | How does the project solve it? | `Uses LLMs to extract structured data from invoice images` |

### Group 3 — Tech Stack

| Placeholder | Question | Default |
|---|---|---|
| `{{LANGUAGE}}` | Primary language? | `Python 3.11+` |
| `{{LINTER}}` | Linter tool? | `Ruff` |
| `{{LINTER_CONFIG}}` | Linter config? | `line-length 100` |
| `{{TEST_FRAMEWORK}}` | Test framework? | `pytest` |
| `{{VALIDATION_LIBRARY}}` | Validation library? | `Pydantic v2` |
| `{{PACKAGE_MANAGER}}` | Package manager? | `uv` |
| `{{CONFIG_FILE}}` | Config file? | `pyproject.toml` |

### Group 4 — Author (for pyproject.toml)

| Placeholder | Question | Example |
|---|---|---|
| `{{AUTHOR_NAME}}` | Author name? | `Arthur Graf` |
| `{{AUTHOR_EMAIL}}` | Author email? | `arthur@example.com` |

### Group 5 — Architecture (Optional)

Tell the user these are optional. If skipped, leave them as placeholders for later.

| Placeholder | Question |
|---|---|
| `{{STAGE_1}}`, `{{TECH_1}}`, `{{PURPOSE_1}}` | First pipeline stage? |
| `{{STAGE_2}}`, `{{TECH_2}}`, `{{PURPOSE_2}}` | Second pipeline stage? |
| `{{STAGE_3}}`, `{{TECH_3}}`, `{{PURPOSE_3}}` | Third pipeline stage? |
| `{{ARCHITECTURE_DIAGRAM}}` | ASCII architecture diagram? |
| `{{MODULE_NAME}}` | Main module folder name? |

### Group 6 — Milestones & Metrics (Optional)

| Placeholder | Question |
|---|---|
| `{{ENV_VAR_1}}`, `{{ENV_PURPOSE_1}}` | Environment variable 1? |
| `{{ENV_VAR_2}}`, `{{ENV_PURPOSE_2}}` | Environment variable 2? |
| `{{DATE_1}}`, `{{MILESTONE_1}}` | First milestone? |
| `{{DATE_2}}`, `{{MILESTONE_2}}` | Second milestone? |
| `{{METRIC_1}}`, `{{TARGET_1}}` | Success metric 1? |
| `{{METRIC_2}}`, `{{TARGET_2}}` | Success metric 2? |

---

## Step 2: Replace Placeholders

After gathering all answers, perform **find-and-replace** across these files:

### Files to update:

1. **`.claude/CLAUDE.md`** — All placeholders
2. **`README.md`** — `{{PROJECT_NAME}}`, `{{PROJECT_DESCRIPTION}}`, `{{REPO_URL}}`, `{{PROJECT_ROOT}}`, `{{ARCHITECTURE_DIAGRAM}}`
3. **`pyproject.toml`** — `{{project-name}}`, `{{PROJECT_DESCRIPTION}}`, `{{AUTHOR_NAME}}`, `{{AUTHOR_EMAIL}}`

### Replacement rules:

- For `pyproject.toml`: convert `{{PROJECT_NAME}}` to lowercase kebab-case for `{{project-name}}`
- Set `{{DATE}}` to today's date automatically (format: `YYYY-MM-DD`)
- If user skipped optional fields, leave the `{{PLACEHOLDER}}` text so `/sync-context` or manual editing can fill them later
- Remove `<!-- comment -->` lines near filled placeholders (they are setup hints)

---

## Step 3: Update Project Structure

If the project already has source files:

1. Run `Glob("**/*.py")`, `Glob("**/*.ts")`, `Glob("**/*.tf")` to detect existing structure
2. Update the Project Structure section in CLAUDE.md to reflect actual directories
3. If no source files exist, leave the template structure as-is

---

## Step 4: Run /sync-context

After replacements, automatically trigger the sync-context workflow to:

- Detect coding patterns from existing code
- Update agent listings
- Refresh command listings
- Detect environment variables from config files

---

## Step 5: Summary Report

Display a summary:

```text
SETUP PROJECT COMPLETE
======================

Project: {name}
Description: {description}
Language: {language}
Package Manager: {package_manager}

Files updated:
  ✓ .claude/CLAUDE.md
  ✓ README.md
  ✓ pyproject.toml

Placeholders filled: {N}/{total}
Remaining (optional): {list of unfilled placeholders}

Next steps:
  1. Create domain agents:  Add .claude/agents/domain/{role}.md
  2. Build knowledge base:  /create-kb {your-technology}
  3. Generate diagrams:     /generate-diagrams architecture
  4. Start building:        /dev "description" or /brainstorm
```

---

## --check Flag

When run with `--check`, scan all template files for remaining `{{...}}` patterns:

```bash
/setup-project --check
```

```text
PLACEHOLDER CHECK
=================

.claude/CLAUDE.md:
  Line 27: {{STAGE_1}} {{TECH_1}} {{PURPOSE_1}}
  Line 28: {{STAGE_2}} {{TECH_2}} {{PURPOSE_2}}
  Line 361: {{ENV_VAR_1}} {{ENV_PURPOSE_1}}

README.md:
  Line 12: {{REPO_URL}}

Total: 9 remaining placeholders (all optional)
```

Use Grep to find all `\{\{[A-Z_]+\}\}` patterns across `.claude/CLAUDE.md`, `README.md`, and `pyproject.toml`.

---

## See Also

| Resource | Path |
|----------|------|
| Setup Guide | `.claude/SETUP.md` |
| Sync Context | `.claude/commands/core/sync-context.md` |
| CLAUDE.md Template | `.claude/CLAUDE.md` |
| Domain Agent Guide | `.claude/agents/domain/_README.md` |
