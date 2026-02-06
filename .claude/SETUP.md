# Setup Guide

> How to adapt this template for your project

---

## Step 1: Copy the Template

Copy the entire `.claude/` folder and `.mcp.json` into your project root:

```bash
cp -r template_claude_code/.claude/ your-project/.claude/
cp template_claude_code/.mcp.json your-project/.mcp.json
```

Also copy the supporting directories if needed:

```bash
cp -r template_claude_code/notes/ your-project/notes/
cp -r template_claude_code/design/ your-project/design/
cp -r template_claude_code/archive/ your-project/archive/
```

---

## Step 2: Customize CLAUDE.md

Open `.claude/CLAUDE.md` and replace all `{{PLACEHOLDERS}}`:

### Required Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{PROJECT_NAME}}` | Your project name | `My E-Commerce Platform` |
| `{{PROJECT_DESCRIPTION}}` | One-line description | `Full-stack marketplace for artisan goods` |
| `{{BUSINESS_PROBLEM}}` | Problem being solved | `Manual order processing causes 2-hour delays` |
| `{{SOLUTION_DESCRIPTION}}` | High-level solution | `Automated order pipeline with real-time inventory` |
| `{{ARCHITECTURE_DIAGRAM}}` | ASCII architecture | *(see examples below)* |
| `{{PROJECT_ROOT}}` | Root folder name | `my-ecommerce` |
| `{{CONFIG_FILE}}` | Config file name | `package.json` or `pyproject.toml` |
| `{{LANGUAGE}}` | Primary language | `TypeScript` or `Python 3.11+` |
| `{{LINTER}}` | Linter tool | `ESLint` or `Ruff` |
| `{{LINTER_CONFIG}}` | Linter config | `eslint.config.js` or `line-length 100` |
| `{{TEST_FRAMEWORK}}` | Test framework | `Jest` or `pytest` |
| `{{VALIDATION_LIBRARY}}` | Validation lib | `Zod` or `Pydantic v2` |
| `{{PACKAGE_MANAGER}}` | Package manager | `npm` or `poetry` |

### Optional Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{{STAGE_N}}`, `{{TECH_N}}`, `{{PURPOSE_N}}` | Tech stack table rows |
| `{{ENV_VAR_N}}`, `{{ENV_PURPOSE_N}}` | Environment variables |
| `{{DATE_N}}`, `{{MILESTONE_N}}` | Project milestones |
| `{{METRIC_N}}`, `{{TARGET_N}}` | Success metrics |
| `{{DATE}}` | Current date |

---

## Step 3: Configure MCP Servers

Edit `.mcp.json` at the project root to match your needs:

### Pre-configured servers

| Server | Needs API Key? | Action |
|--------|---------------|--------|
| **context7** | No | Works out of the box |
| **exa** | Yes (`EXA_API_KEY`) | Set env var or remove if not needed |
| **github** | Yes (`GITHUB_TOKEN`) | Set env var or remove if not needed |
| **playwright** | No | Works out of the box |
| **sequential-thinking** | No | Works out of the box |

### Set API keys

```bash
# Option 1: Export in your shell profile (~/.bashrc, ~/.zshrc)
export EXA_API_KEY="your-key-here"
export GITHUB_TOKEN="your-token-here"

# Option 2: Use .env file (already in .gitignore)
echo 'EXA_API_KEY=your-key-here' >> .env
echo 'GITHUB_TOKEN=your-token-here' >> .env
```

### Remove servers you don't need

If you don't use a server, remove its block from `.mcp.json`. Fewer servers = faster Claude Code startup.

### Add more servers

```json
{
  "sentry": {
    "command": "npx",
    "args": ["-y", "@sentry/mcp-server-sentry"],
    "env": { "SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}" }
  }
}
```

---

## Step 4: Create Domain Agents

Add project-specific agents in `.claude/agents/domain/`:

```bash
# Copy the template
cp .claude/agents/_template.md.example .claude/agents/domain/my-specialist.md

# Edit to match your domain
```

See `.claude/agents/domain/_README.md` for examples by project type.

---

## Step 5: Create Knowledge Base Domains

Use the `/create-kb` command to create domain-specific knowledge:

```bash
# Interactive: the kb-architect agent will guide you
/create-kb "React"
/create-kb "PostgreSQL"
/create-kb "Docker"
```

Or create manually following `.claude/kb/_README.md`.

---

## Step 6: Install Third-Party Skills (Optional)

Browse skills at [skills.sh](https://skills.sh) and install with:

```bash
npx add-skill <owner/repo>
```

Skills install into `.claude/skills/<name>/SKILL.md` and are automatically discovered by Claude.

### Pre-included skills

| Skill | Invocation | Auto? |
|-------|-----------|-------|
| `security-guidance` | Automatic or `/security-guidance` | Yes |
| `code-review` | `/code-review` | Manual |
| `commit` | `/commit` | Manual |
| `pr-review` | `/pr-review` | Manual |

---

## Step 7: Update Project Structure

Edit the "Project Structure" section in `CLAUDE.md` to reflect your actual directory layout. Remove sections that don't apply and add project-specific sections.

---

## Step 8: Add Meeting Notes

Use the templates in `notes/` (or `.claude/notes/`) for project meetings:

1. Copy and rename `01-meeting-notes.md` for each meeting
2. Fill in the sections as meetings occur
3. After key meetings, consolidate into `summary-requirements.md`

---

## Step 9: Start Building

### Quick Task (Level 2 - Dev Loop)

```bash
/dev "I want to build a user authentication module"
```

### Complex Feature (Level 3 - SDD)

```bash
/brainstorm "Build a real-time notification system"
# then follow: /define → /design → /build → /ship
```

---

## Checklist

After setup, verify:

- [ ] `CLAUDE.md` has all `{{PLACEHOLDERS}}` replaced
- [ ] `.mcp.json` configured (removed unused servers, set API keys)
- [ ] Project structure section matches your actual layout
- [ ] At least one domain agent created in `agents/domain/`
- [ ] At least one KB domain created (optional but recommended)
- [ ] Meeting notes templates ready for use
- [ ] Tech stack and coding standards sections are accurate
- [ ] Skills reviewed (remove or add as needed)

---

## Architecture Diagram Examples

### Web Application

```text
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Client  │──▶│   API    │──▶│ Service  │──▶│ Database │
│ (React)  │   │ (Express)│   │  Layer   │   │(Postgres)│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Data Pipeline

```text
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Source  │──▶│  Ingest  │──▶│Transform │──▶│  Store   │
│  (APIs)  │   │ (Kafka)  │   │ (Spark)  │   │   (DW)   │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### Mobile App

```text
┌──────────┐   ┌──────────┐   ┌──────────┐
│  Mobile  │──▶│  BFF /   │──▶│ Backend  │
│  (RN)    │   │   API    │   │Services  │
└──────────┘   └──────────┘   └──────────┘
```

---

## Removing Unused Components

### Agents

```bash
# Remove data-engineering agents for a frontend project
rm -rf .claude/agents/data-engineering/

# Remove AWS agents for a GCP project
rm -rf .claude/agents/aws/
```

### Skills

```bash
# Remove a skill you don't need
rm -rf .claude/skills/pr-review/
```

Then update the relevant tables in `CLAUDE.md` accordingly.

---

## Need Help?

- **SDD Workflow:** `.claude/sdd/_index.md`
- **Dev Loop:** `.claude/dev/_index.md`
- **Agent Template:** `.claude/agents/_template.md.example`
- **KB Guide:** `.claude/kb/_README.md`
- **Skills Guide:** `.claude/skills/_README.md`
- **MCP Config:** `.mcp.json`
