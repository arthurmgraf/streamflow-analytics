# Skills Directory

> Reusable capabilities for Claude Code. Skills extend what Claude can do.

---

## How Skills Work

Skills are `SKILL.md` files with YAML frontmatter + markdown instructions. Claude reads skill descriptions and **automatically invokes** the right skill when your request matches.

```text
.claude/skills/
├── _README.md              # This file
├── security-guidance/      # Security best practices
│   └── SKILL.md
├── code-review/            # Code review workflow
│   └── SKILL.md
├── commit-commands/        # Git commit assistance
│   └── SKILL.md
└── pr-review/              # Pull request review
    └── SKILL.md
```

---

## SKILL.md Format

```yaml
---
name: my-skill                        # becomes /my-skill slash command
description: What this does and when   # Claude uses this to auto-invoke
disable-model-invocation: false        # true = manual only (/my-skill)
user-invocable: true                   # false = only Claude can invoke
allowed-tools: Read, Grep, Glob       # restrict available tools
context: fork                          # run in isolated subagent (optional)
model: opus                            # model override (optional)
---

Your instructions here...
```

---

## Auto-Invocation

By default, Claude reads all skill descriptions and loads them when relevant:

| Setting | You invoke | Claude invokes | Use case |
|---------|-----------|---------------|----------|
| *(default)* | Yes (`/name`) | Yes (auto) | General skills |
| `disable-model-invocation: true` | Yes | No | Dangerous ops (deploy, commit) |
| `user-invocable: false` | No | Yes | Background knowledge |

---

## Installing Third-Party Skills

```bash
# From skills.sh marketplace
npx add-skill <owner/repo>

# From any git URL
npx add-skill https://github.com/user/skill-repo
```

Skills install into `.claude/skills/<name>/SKILL.md`.

---

## Creating Custom Skills

1. Create a directory: `mkdir -p .claude/skills/my-skill`
2. Create `SKILL.md` with frontmatter + instructions
3. Optionally add supporting files (templates, scripts, examples)
4. Test with `/my-skill` or by asking Claude something matching the description

### Tips

- Keep `SKILL.md` under 500 lines
- One focused skill per concern
- Write clear descriptions (max 200 chars) -- Claude uses these to decide when to invoke
- Move detailed reference material to separate files in the skill directory

---

## Skills vs Commands vs Agents

| Feature | `.claude/commands/` | `.claude/skills/` | `.claude/agents/` |
|---------|--------------------|--------------------|-------------------|
| Slash commands | Yes | Yes | No (Task tool) |
| Supporting files | No | Yes (whole directory) | No (single .md) |
| Auto-invocation | Yes | Yes (richer control) | Yes (via description) |
| Subagent execution | No | Yes (`context: fork`) | Yes (always fork) |
| Frontmatter | Basic | Full (tools, model, hooks) | Full |

**Recommendation:** Use `skills/` for new additions. Existing `commands/` continue to work.

---

## References

- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills)
- [Agent Skills Standard](https://agentskills.io)
- [Skills Marketplace](https://skills.sh)
- [add-skill CLI](https://add-skill.org)
