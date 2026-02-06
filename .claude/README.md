# Claude Code Ecosystem Template

> Universal `.claude/` template for any project — AgentSpec 4.2 + Dev Loop + Knowledge Base

---

## What's Included

This template provides a complete Claude Code ecosystem that works with **any project type** — frontend, backend, data engineering, mobile, ML, and more.

### Components

| Component | Files | Purpose |
|-----------|-------|---------|
| **Agents** | 35 universal + domain templates | Specialized AI agents for development |
| **Commands** | 13 slash commands | Workflow automation (`/brainstorm`, `/define`, `/build`, etc.) |
| **SDD** | 5 templates + architecture | Spec-Driven Development (Level 3) |
| **Dev Loop** | 4 templates + framework | Agentic Development (Level 2) |
| **KB** | 7 domain templates | Knowledge Base creation system |
| **CLAUDE.md** | Template with `{{placeholders}}` | Project context file |

---

## Quick Start

1. **Copy** this `.claude/` folder into your project root
2. **Follow** the [SETUP.md](SETUP.md) guide to customize
3. **Start building** with `/dev` or `/brainstorm`

---

## The 3-Level Development Spectrum

```text
LEVEL 1              LEVEL 2              LEVEL 3
Vibe Coding          Dev Loop             Spec-Driven Dev
───────────          ────────             ───────────────
Just prompts         PROMPT.md driven     5-phase pipeline
No structure         Verification loops   Full traceability
Hope it works        Agent leverage       Quality gates

Command: (none)      Command: /dev        Commands: /brainstorm → /ship
```

### When to Use Each

| Scenario | Level 2 (/dev) | Level 3 (SDD) |
|----------|----------------|---------------|
| KB building | X | |
| Prototypes | X | |
| Single features | X | |
| Utilities/parsers | X | |
| Multi-component features | | X |
| Production systems | | X |
| Team projects | | X |
| Full audit trail needed | | X |

---

## Agent Categories (35 Universal)

| Category | Count | Agents |
|----------|-------|--------|
| **Workflow** | 6 | brainstorm, define, design, build, ship, iterate |
| **Code Quality** | 6 | code-reviewer, code-cleaner, code-documenter, dual-reviewer, python-developer, test-generator |
| **Data Engineering** | 8 | spark-specialist, spark-troubleshooter, spark-performance-analyzer, spark-streaming-architect, lakeflow-architect, lakeflow-expert, lakeflow-pipeline-builder, medallion-architect |
| **AI/ML** | 4 | llm-specialist, genai-architect, ai-prompt-specialist, ai-data-engineer |
| **AWS** | 4 | aws-deployer, aws-lambda-architect, lambda-builder, ci-cd-specialist |
| **Communication** | 3 | adaptive-explainer, meeting-analyst, the-planner |
| **Exploration** | 2 | codebase-explorer, kb-architect |
| **Dev** | 2 | prompt-crafter, dev-loop-executor |
| **Domain** | 0+ | *Add your own project-specific agents* |

---

## Folder Structure

```text
.claude/
├── CLAUDE.md                    # Project context (customize with {{placeholders}})
├── README.md                    # This file
├── SETUP.md                     # Setup guide
│
├── agents/                      # 35 universal + domain templates
│   ├── _template.md.example     # Agent creation template
│   ├── ai-ml/                   # 4 AI/ML specialists
│   ├── aws/                     # 4 AWS/cloud specialists
│   ├── code-quality/            # 6 code review/testing
│   ├── communication/           # 3 documentation/planning
│   ├── data-engineering/        # 8 Spark/Lakeflow/Medallion
│   ├── dev/                     # 2 Dev Loop agents
│   ├── domain/                  # Your project-specific agents
│   ├── exploration/             # 2 codebase exploration
│   └── workflow/                # 6 SDD pipeline agents
│
├── commands/                    # 13 slash commands
│   ├── core/                    # /memory, /sync-context, /readme-maker
│   ├── dev/                     # /dev (Dev Loop)
│   ├── knowledge/               # /create-kb
│   ├── review/                  # /review
│   └── workflow/                # /brainstorm, /define, /design, /build, /ship, /iterate, /create-pr
│
├── sdd/                         # Spec-Driven Development framework
│   ├── _index.md                # SDD documentation
│   ├── readme.md                # SDD overview
│   ├── architecture/            # ARCHITECTURE.md + WORKFLOW_CONTRACTS.yaml
│   ├── templates/               # 5 document templates
│   ├── features/                # Active feature documents
│   ├── reports/                 # Build reports
│   ├── archive/                 # Shipped features
│   └── examples/                # Add your examples here
│
├── dev/                         # Dev Loop framework
│   ├── _index.md                # Dev Loop documentation
│   ├── readme.md                # Dev Loop overview
│   ├── templates/               # 4 PROMPT/PROGRESS templates
│   ├── tasks/                   # Active PROMPT files
│   ├── progress/                # Memory bridge files
│   ├── logs/                    # Execution logs
│   └── examples/                # Add your examples here
│
└── kb/                          # Knowledge Base
    ├── _index.yaml              # Domain registry
    ├── _README.md               # KB usage guide
    └── _templates/              # 7 domain creation templates
```

---

## Key Files

| File | Purpose | Action |
|------|---------|--------|
| `CLAUDE.md` | Project context for Claude | **Customize** with your project details |
| `SETUP.md` | Step-by-step setup guide | **Follow** to adapt the template |
| `agents/domain/` | Project-specific agents | **Create** agents for your domain |
| `kb/_index.yaml` | KB domain registry | **Populate** as you add domains |

---

## References

| Resource | Location |
|----------|----------|
| AgentSpec 4.2 Docs | `.claude/sdd/_index.md` |
| Dev Loop Docs | `.claude/dev/_index.md` |
| Agent Template | `.claude/agents/_template.md.example` |
| KB Guide | `.claude/kb/_README.md` |
| Domain Agent Guide | `.claude/agents/domain/_README.md` |
