# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

---

## Project Context

**Business Problem:** {{BUSINESS_PROBLEM}}

**Solution:** {{SOLUTION_DESCRIPTION}}

**Requirements:** See [notes/summary-requirements.md](notes/summary-requirements.md) for consolidated requirements.

---

## Architecture Overview

<!-- Replace with your project's architecture diagram -->

```text
{{ARCHITECTURE_DIAGRAM}}
```

| Stage | Technology | Purpose |
| ----- | ---------- | ------- |
| {{STAGE_1}} | {{TECH_1}} | {{PURPOSE_1}} |
| {{STAGE_2}} | {{TECH_2}} | {{PURPOSE_2}} |
| {{STAGE_3}} | {{TECH_3}} | {{PURPOSE_3}} |

---

## Project Structure

<!-- Update to reflect your actual project layout -->

```text
{{PROJECT_ROOT}}/
├── src/                           # Main source code
│   ├── __init__.py
│   ├── {{MODULE_NAME}}/           # Your main module
│   └── tests/                     # Module-specific tests
│       ├── unit/
│       ├── integration/
│       └── fixtures/
│
├── tests/                         # Project-wide test suites
│   ├── conftest.py                # Shared test fixtures
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── smoke/                     # End-to-end smoke tests
│       ├── stages/                # Pipeline test stages
│       ├── validators/            # Result validation
│       ├── config/                # Test configuration
│       └── fixtures/              # Test data
│
├── functions/                     # Cloud functions (serverless)
│   ├── src/
│   │   ├── functions/             # Individual cloud functions
│   │   │   └── {{function}}/      # One folder per function
│   │   └── shared/                # Shared utilities
│   │       ├── adapters/          # External service adapters
│   │       ├── schemas/           # Data models
│   │       └── utils/             # Logging, config, helpers
│   ├── tests/                     # Function tests
│   ├── deploy/                    # Deployment configs
│   └── scripts/                   # Helper scripts
│
├── infra/                         # Infrastructure as Code
│   ├── modules/                   # Reusable IaC modules
│   ├── environments/              # Environment configs
│   │   ├── dev/
│   │   └── prod/
│   └── scripts/                   # IaC helper scripts
│
├── gen/                           # Code generation & synthetic data
│   ├── assets/                    # Static assets
│   ├── samples/                   # Generated samples
│   ├── src/                       # Generator source code
│   ├── templates/                 # Generation templates
│   └── tests/                     # Generator tests
│
├── design/                        # Architecture design documents
│   └── ...
│
├── notes/                         # Project meeting notes
│   ├── 01-meeting-notes.md
│   ├── 02-meeting-notes.md
│   ├── 03-meeting-notes.md
│   └── summary-requirements.md
│
├── archive/                       # Historical versions
│   └── ...
│
├── .claude/                       # Claude Code AI ecosystem
│   ├── CLAUDE.md                  # This file (project context)
│   ├── settings.json              # Tool permissions
│   ├── agents/                    # 36+ specialized agents
│   │   ├── ai-ml/                 # AI/ML specialists (4)
│   │   ├── aws/                   # AWS/cloud specialists (4)
│   │   ├── code-quality/          # Code review, testing (7)
│   │   ├── communication/         # Documentation, planning (3)
│   │   ├── data-engineering/      # Spark, Lakeflow, Medallion (8)
│   │   ├── dev/                   # Dev Loop agents (2)
│   │   ├── domain/                # Project-specific agents (add yours)
│   │   ├── exploration/           # Codebase exploration (2)
│   │   └── workflow/              # SDD pipeline agents (6)
│   │
│   ├── skills/                    # Reusable skills (auto-invoked)
│   │   ├── security-guidance/     # OWASP & security best practices
│   │   ├── code-review/           # Structured code review
│   │   ├── commit-commands/       # Conventional commits
│   │   └── pr-review/             # Pull request review
│   │
│   ├── commands/                  # 13 slash commands
│   │   ├── core/                  # /memory, /sync-context, /readme-maker
│   │   ├── dev/                   # /dev (Dev Loop)
│   │   ├── knowledge/             # /create-kb
│   │   ├── review/                # /review
│   │   └── workflow/              # SDD commands
│   │
│   ├── kb/                        # Knowledge Base
│   │   ├── _templates/            # 7 templates for domain creation
│   │   └── ...                    # Add domains with /create-kb
│   │
│   ├── sdd/                       # Spec-Driven Development (Level 3)
│   │   ├── architecture/          # Workflow contracts + architecture
│   │   ├── templates/             # 5 document templates
│   │   ├── features/              # Active feature documents
│   │   ├── reports/               # Build reports
│   │   ├── archive/               # Shipped features
│   │   └── examples/              # Reference examples
│   │
│   └── dev/                       # Dev Loop (Level 2)
│       ├── templates/             # 4 PROMPT/PROGRESS templates
│       ├── tasks/                 # Active PROMPT files
│       ├── progress/              # Memory bridge
│       ├── logs/                  # Execution logs
│       └── examples/              # Reference examples
│
├── .mcp.json                      # MCP server configuration
├── pyproject.toml                 # Python project configuration
├── .gitignore                     # Git ignore rules
├── LICENSE                        # License file
└── README.md                      # Project README
```

---

## Development Workflows

### AgentSpec 4.2 (Spec-Driven Development)

5-phase structured workflow for features requiring traceability:

```text
/brainstorm → /define → /design → /build → /ship
  (Opus)      (Opus)    (Opus)   (Sonnet)  (Haiku)
```

| Command | Phase | Purpose |
|---------|-------|---------|
| `/brainstorm` | 0 | Explore ideas through dialogue (optional) |
| `/define` | 1 | Capture and validate requirements |
| `/design` | 2 | Create architecture and specification |
| `/build` | 3 | Execute implementation with verification |
| `/ship` | 4 | Archive with lessons learned |
| `/iterate` | Any | Update documents when changes needed |

**Artifacts:** `.claude/sdd/features/` and `.claude/sdd/archive/`

### Dev Loop (Level 2 Agentic Development)

Structured iteration with PROMPT.md files and session recovery:

```bash
# Let the crafter guide you
/dev "I want to build a date parser utility"

# Execute existing PROMPT
/dev tasks/PROMPT_DATE_PARSER.md

# Resume interrupted session
/dev tasks/PROMPT_DATE_PARSER.md --resume
```

**When to use:**
- KB building
- Prototypes
- Single features
- Utilities and parsers

---

## Agent Usage Guidelines

### Available Agents by Category

| Category | Agents | Use When |
| -------- | ------ | -------- |
| **Workflow** | brainstorm-agent, define-agent, design-agent, build-agent, ship-agent, iterate-agent | Building features with SDD |
| **Code Quality** | code-reviewer, code-cleaner, code-simplifier, code-documenter, dual-reviewer, python-developer, test-generator | Improving code quality |
| **Data Engineering** | spark-specialist, spark-troubleshooter, spark-performance-analyzer, spark-streaming-architect, lakeflow-architect, lakeflow-expert, lakeflow-pipeline-builder, medallion-architect | Spark/Lakeflow work |
| **AI/ML** | llm-specialist, genai-architect, ai-prompt-specialist, ai-data-engineer | LLM prompts, AI systems |
| **AWS** | aws-deployer, aws-lambda-architect, lambda-builder, ci-cd-specialist | AWS deployments |
| **Communication** | adaptive-explainer, meeting-analyst, the-planner | Explanations, planning |
| **Domain** | *(add your project-specific agents)* | Project-specific tasks |
| **Exploration** | codebase-explorer, kb-architect | Codebase exploration, KB creation |
| **Dev** | prompt-crafter, dev-loop-executor | Dev Loop workflow |

### Agent Reference Syntax

In PROMPT.md files, reference agents with `@agent-name`:

```markdown
### CORE
- [ ] @kb-architect: Create Redis KB domain
- [ ] @python-developer: Implement cache wrapper
- [ ] @test-generator: Add unit tests
```

---

## Skills (Auto-Invoked)

Skills extend Claude's capabilities. Claude loads them automatically when relevant, or invoke directly with `/skill-name`.

| Skill | Auto-Invoke | Purpose |
| ----- | ----------- | ------- |
| `security-guidance` | Yes | OWASP best practices, vulnerability analysis |
| `code-review` | Manual (`/code-review`) | Structured code review with severity ratings |
| `commit` | Manual (`/commit`) | Conventional commit format assistance |
| `pr-review` | Manual (`/pr-review`) | Pull request analysis and review |

### Installing Third-Party Skills

```bash
# From skills.sh marketplace (35,000+ available)
npx add-skill <owner/repo>
```

See [.claude/skills/_README.md](.claude/skills/_README.md) for creating custom skills.

---

## MCP Servers (Pre-configured)

MCP servers connect Claude to external tools. Configuration in `.mcp.json`:

| Server | Purpose | Env Var Required |
| ------ | ------- | ---------------- |
| **context7** | Up-to-date library documentation | None |
| **sequential-thinking** | Complex problem decomposition | None |
| **memory** | Persistent memory across sessions (knowledge graph) | None |
| **fetch** | Fetch web content and convert to markdown | None |
| **playwright** | Browser automation and E2E testing | None |
| **github** | PR/issue management, CI/CD, commits | `GITHUB_TOKEN` |
| **brave-search** | Web search (2000 queries/month free) | `BRAVE_API_KEY` |

### Adding More MCP Servers

Edit `.mcp.json` at the project root. Recommended additions based on your stack:

| Server | Install | Use Case |
| ------ | ------- | -------- |
| Sentry | `@sentry/mcp-server-sentry` | Error tracking, debugging |
| Docker | `@modelcontextprotocol/server-docker` | Container management |
| PostgreSQL | `@modelcontextprotocol/server-postgres` | Database exploration |
| Exa | `exa-mcp-server` | AI-powered code search (requires API key) |

---

## Coding Standards

### Language: {{LANGUAGE}}

<!-- Customize these standards for your project -->

- **Style:** {{LINTER}} ({{LINTER_CONFIG}})
- **Testing:** {{TEST_FRAMEWORK}}
- **Validation:** {{VALIDATION_LIBRARY}}
- **Package Management:** {{PACKAGE_MANAGER}}
- **Type Hints:** Required on all function signatures

### Code Quality Rules

1. **Type hints required** - All function signatures must be typed
2. **Structured logging** - Use structured JSON logging in production
3. **Test coverage** - All new code must have tests
4. **Self-documenting names** - Prefer clear names over comments
5. **Config over hardcode** - Use configuration files, not magic values

---

## Commands

| Command | Purpose |
| ------- | ------- |
| `/brainstorm` | Explore ideas through collaborative dialogue |
| `/define` | Capture and validate requirements |
| `/design` | Create technical architecture |
| `/build` | Execute implementation |
| `/ship` | Archive completed features |
| `/iterate` | Update documents mid-stream |
| `/dev` | Dev Loop for structured iteration |
| `/create-kb` | Create knowledge base domains |
| `/review` | Code review workflow |
| `/create-pr` | Create pull requests |
| `/memory` | Save session insights |
| `/generate-diagrams` | Generate architecture diagrams (Excalidraw) |
| `/setup-project` | Adapt this template to a new project |
| `/sync-context` | Update CLAUDE.md with project context |
| `/readme-maker` | Generate comprehensive README |

### Skills (slash commands)

| Skill | Purpose |
| ----- | ------- |
| `/code-review` | Structured code review |
| `/commit` | Conventional commit assistance |
| `/pr-review` | Pull request review |
| `/security-guidance` | Security best practices |

---

## Knowledge Base

<!-- Add your domains here as you create them with /create-kb -->

| Domain | Purpose | Entry Point |
| ------ | ------- | ----------- |
| *(empty - use `/create-kb` to add domains)* | | |

### KB Structure

```text
.claude/kb/{domain}/
├── index.md           # Domain overview
├── quick-reference.md # Cheat sheet
├── concepts/          # Core concepts
├── patterns/          # Implementation patterns
└── specs/             # YAML specifications (optional)
```

---

## Shipped Features (SDD Archive)

<!-- Features will appear here as you ship them with /ship -->

| Feature | Shipped | Description |
| ------- | ------- | ----------- |
| *(none yet)* | | |

---

## Environment Configuration

### Required Environment Variables

<!-- List your project's environment variables -->

| Variable | Purpose |
| -------- | ------- |
| `{{ENV_VAR_1}}` | {{ENV_PURPOSE_1}} |
| `{{ENV_VAR_2}}` | {{ENV_PURPOSE_2}} |

### MCP Environment Variables (optional)

| Variable | Purpose |
| -------- | ------- |
| `GITHUB_TOKEN` | GitHub MCP server authentication (free at github.com/settings/tokens) |
| `BRAVE_API_KEY` | Brave Search API (free tier: 2000/month at brave.com/search/api/) |

---

## Important Dates

<!-- Add your project milestones -->

| Date | Milestone |
| ---- | --------- |
| {{DATE_1}} | {{MILESTONE_1}} |
| {{DATE_2}} | {{MILESTONE_2}} |

---

## Success Metrics

<!-- Define measurable success criteria -->

| Metric | Target |
| ------ | ------ |
| {{METRIC_1}} | {{TARGET_1}} |
| {{METRIC_2}} | {{TARGET_2}} |

---

## Getting Help

- **All Commands & Skills:** See [.claude/COMMANDS_REFERENCE.md](.claude/COMMANDS_REFERENCE.md)
- **SDD Workflow:** See [.claude/sdd/_index.md](.claude/sdd/_index.md)
- **Dev Loop:** See [.claude/dev/_index.md](.claude/dev/_index.md)
- **Agents:** Browse [.claude/agents/](.claude/agents/)
- **Skills:** See [.claude/skills/_README.md](.claude/skills/_README.md)
- **MCP Config:** See [.mcp.json](../.mcp.json)
- **KB Index:** See [.claude/kb/_index.yaml](.claude/kb/_index.yaml)
- **KB Guide:** See [.claude/kb/_README.md](.claude/kb/_README.md)
- **Domain Agents:** See [.claude/agents/domain/_README.md](.claude/agents/domain/_README.md)
- **Setup Guide:** See [.claude/SETUP.md](.claude/SETUP.md)

---

## Version History

| Date | Changes |
| ---- | ------- |
| {{DATE}} | Initial CLAUDE.md created from template |