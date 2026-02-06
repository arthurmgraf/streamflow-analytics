# Commands & Skills Reference

> Tudo que voce pode usar neste template -- comandos, skills, agentes e MCPs.

---

## 1. Slash Commands (built-in do template)

Comandos que voce digita diretamente na conversa com `/comando`:

### Workflow SDD (Spec-Driven Development)

- `/brainstorm` -- Explorar ideias com dialogo colaborativo (Opus)
- `/define` -- Capturar e validar requisitos (Opus)
- `/design` -- Criar arquitetura tecnica (Opus)
- `/build` -- Executar implementacao com verificacao (Sonnet)
- `/ship` -- Arquivar feature completa com licoes aprendidas (Haiku)
- `/iterate` -- Atualizar documentos durante o desenvolvimento
- `/create-pr` -- Criar pull requests

### Core

- `/memory` -- Salvar insights da sessao atual
- `/sync-context` -- Atualizar CLAUDE.md com contexto do projeto
- `/readme-maker` -- Gerar README.md completo

### Dev Loop

- `/dev` -- Iteracao estruturada com PROMPT.md files

### Quality

- `/review` -- Code review workflow
- `/create-kb` -- Criar dominios de knowledge base

---

## 2. Skills Pre-incluidas (custom)

Skills locais criadas no template em `.claude/skills/`:

- `/security-guidance` -- Boas praticas OWASP, analise de vulnerabilidades (auto-invocada)
- `/code-review` -- Code review estruturado com severidade (manual)
- `/commit` -- Commits no formato Conventional Commits (manual)
- `/pr-review` -- Revisao de Pull Requests (manual)

---

## 3. Skills do skills.sh (recomendadas para instalar)

Instale com `npx add-skill <owner/repo>`. Todas funcionam autonomamente -- o Claude as invoca quando relevante.

### Python & Backend

- `npx add-skill wshobson/agents` -- python-performance-optimization (1.7K installs)
- `npx add-skill wshobson/agents` -- python-testing-patterns (1.4K installs)
- `npx add-skill wshobson/agents` -- async-python-patterns (1.2K installs)
- `npx add-skill wshobson/agents` -- python-packaging (947 installs)
- `npx add-skill wshobson/agents` -- fastapi-templates (1.4K installs)
- `npx add-skill wshobson/agents` -- nodejs-backend-patterns (1.6K installs)
- `npx add-skill supabase/agent-skills` -- supabase-postgres-best-practices (9K installs)
- `npx add-skill better-auth/skills` -- better-auth-best-practices (6.4K installs)
- `npx add-skill inference-sh/skills` -- python-executor (433 installs)

### Frontend & UI/UX

- `npx add-skill vercel-labs/agent-skills` -- vercel-react-best-practices (83.9K installs)
- `npx add-skill vercel-labs/agent-skills` -- web-design-guidelines (63.5K installs)
- `npx add-skill anthropics/skills` -- frontend-design (33.2K installs)
- `npx add-skill nextlevelbuilder/ui-ux-pro-max-skill` -- ui-ux-pro-max (10.4K installs)
- `npx add-skill anthropics/skills` -- web-artifacts-builder (3.1K installs)
- `npx add-skill anthropics/skills` -- theme-factory (3.3K installs)
- `npx add-skill wshobson/agents` -- tailwind-design-system (2.5K installs)
- `npx add-skill giuseppe-trisciuoglio/developer-kit` -- shadcn-ui (2.3K installs)
- `npx add-skill ibelick/ui-skills` -- baseline-ui (862 installs)
- `npx add-skill ibelick/ui-skills` -- fixing-accessibility (748 installs)

### Seguranca

- `npx add-skill sickn33/antigravity-awesome-skills` -- security-review (687 installs)
- `npx add-skill wshobson/agents` -- security-requirement-extraction (763 installs)
- `npx add-skill wshobson/agents` -- k8s-security-policies (794 installs)
- `npx add-skill sickn33/antigravity-awesome-skills` -- api-security-best-practices (387 installs)
- `npx add-skill trailofbits/skills` -- secure-workflow-guide (365 installs)
- `npx add-skill trailofbits/skills` -- semgrep (381 installs)

### Testing

- `npx add-skill anthropics/skills` -- webapp-testing (4.7K installs)
- `npx add-skill obra/superpowers` -- test-driven-development (3.8K installs)
- `npx add-skill wshobson/agents` -- e2e-testing-patterns (1.3K installs)
- `npx add-skill wshobson/agents` -- javascript-testing-patterns (1.1K installs)
- `npx add-skill sickn33/antigravity-awesome-skills` -- playwright-skill (544 installs)
- `npx add-skill trailofbits/skills` -- property-based-testing (364 installs)

### Git & DevOps

- `npx add-skill obra/superpowers` -- using-git-worktrees (2.7K installs)
- `npx add-skill wshobson/agents` -- git-advanced-workflows (998 installs)
- `npx add-skill wshobson/agents` -- github-actions-templates (1.2K installs)
- `npx add-skill github/awesome-copilot` -- git-commit (432 installs)

### Frameworks Especificos

- `npx add-skill kadajett/agent-nestjs-skills` -- nestjs-best-practices (1.4K installs)
- `npx add-skill jeffallan/claude-skills` -- laravel-specialist (477 installs)
- `npx add-skill elysiajs/skills` -- elysiajs (566 installs)
- `npx add-skill analogjs/angular-skills` -- angular-testing (368 installs)
- `npx add-skill vuejs-ai/skills` -- vue-testing-best-practices (621 installs)

---

## 4. Agentes Especializados (36 subagentes)

Agentes sao invocados automaticamente pelo Claude via Task tool. Voce nao precisa chamar diretamente -- o Claude decide quando delegar.

### Code Quality (7)

- `code-reviewer` -- Revisao de codigo com scoring
- `code-cleaner` -- Remocao de comentarios, DRY, modernizacao
- `code-simplifier` -- Simplificacao de codigo mantendo funcionalidade
- `code-documenter` -- Documentacao e README
- `dual-reviewer` -- Review duplo (CodeRabbit + Claude)
- `python-developer` -- Codigo Python: dataclasses, type hints, generators
- `test-generator` -- Testes pytest com fixtures e edge cases

### AI/ML (4)

- `llm-specialist` -- Prompts estruturados, chain-of-thought
- `genai-architect` -- Arquitetura de sistemas AI multi-agente
- `ai-prompt-specialist` -- Otimizacao de prompts e extracao
- `ai-data-engineer` -- Pipelines de dados e arquiteturas cloud

### AWS (4)

- `aws-deployer` -- Deploy SAM CLI e AWS CLI
- `aws-lambda-architect` -- SAM templates com IAM least-privilege
- `lambda-builder` -- Lambda handlers Python com Powertools
- `ci-cd-specialist` -- Azure DevOps, Terraform, DABs

### Data Engineering (8)

- `spark-specialist` -- PySpark performance e arquitetura
- `spark-troubleshooter` -- Debug de erros Spark
- `spark-performance-analyzer` -- Profiling e bottleneck detection
- `spark-streaming-architect` -- Structured Streaming e Kafka
- `lakeflow-architect` -- Medallion Architecture com DLT
- `lakeflow-expert` -- DLT operations e CDC
- `lakeflow-pipeline-builder` -- Bronze/Silver/Gold pipelines
- `medallion-architect` -- Design de lakehouse

### Communication (3)

- `adaptive-explainer` -- Explicacoes adaptadas para qualquer audiencia
- `meeting-analyst` -- Analise de reunioes e extracao de decisoes
- `the-planner` -- Planejamento estrategico e roadmaps

### Exploration (2)

- `codebase-explorer` -- Analise de codebase com Executive Summary
- `kb-architect` -- Criacao de dominios Knowledge Base

### Workflow SDD (6)

- `brainstorm-agent` -- Exploracao de ideias
- `define-agent` -- Captura de requisitos
- `design-agent` -- Design de arquitetura
- `build-agent` -- Implementacao com verificacao
- `ship-agent` -- Arquivamento e licoes
- `iterate-agent` -- Atualizacao de documentos

### Dev Loop (2)

- `prompt-crafter` -- Builder interativo de PROMPT.md
- `dev-loop-executor` -- Execucao de Dev Loop com recovery

### Domain (customizavel)

- Adicione seus agentes em `.claude/agents/domain/`

---

## 5. MCP Servers (ferramentas externas)

Configurados em `.mcp.json`. Funcionam automaticamente.

- **context7** -- Documentacao atualizada de bibliotecas (sem API key)
- **exa** -- Busca AI-powered na web (requer `EXA_API_KEY`)
- **github** -- PRs, issues, CI/CD, commits (requer `GITHUB_TOKEN`)
- **playwright** -- Automacao de browser e testes E2E (sem API key)
- **sequential-thinking** -- Decomposicao de problemas complexos (sem API key)

### MCPs adicionais recomendados (instale no .mcp.json)

- **sentry** -- Error tracking e debugging
- **docker** -- Gerenciamento de containers
- **postgresql** -- Exploracao de banco de dados
- **brave-search** -- Busca web com privacidade

---

## 6. Autonomia -- O que funciona sozinho?

| Componente | Autonomo? | Como funciona |
|------------|-----------|---------------|
| **Agentes** | Sim | Claude decide quando delegar tarefas a subagentes |
| **Skills (auto-invoke)** | Sim | `security-guidance` carrega automaticamente ao revisar seguranca |
| **Skills (manual)** | Nao | `/commit`, `/code-review`, `/pr-review` precisam ser chamados por voce |
| **MCP Servers** | Sim | Claude usa automaticamente quando precisa buscar docs, PRs, etc. |
| **Slash Commands** | Nao | Voce digita `/brainstorm`, `/build`, etc. manualmente |
| **Skills do skills.sh** | Depende | Se `disable-model-invocation` for false (padrao), Claude auto-invoca |

### O que e totalmente autonomo

Ao abrir o Claude Code neste template, ele automaticamente:

1. Le `CLAUDE.md` e entende o contexto do projeto
2. Reconhece todos os 36 agentes e delega tarefas quando necessario
3. Carrega descricoes de todas as skills e as usa quando relevante
4. Usa MCP servers para buscar documentacao, gerenciar PRs, etc.
5. Aplica `security-guidance` ao revisar codigo sensivel

### O que voce precisa invocar

1. Workflows SDD: `/brainstorm` -> `/define` -> `/design` -> `/build` -> `/ship`
2. Dev Loop: `/dev "task description"`
3. Reviews explicitos: `/code-review`, `/pr-review`, `/commit`
4. Gestao: `/memory`, `/sync-context`, `/create-kb`

---

## Quick Start

```bash
# 1. Instalar skills populares (escolha as que fazem sentido)
npx add-skill wshobson/agents                    # Python, backend, testing
npx add-skill vercel-labs/agent-skills            # React, frontend
npx add-skill anthropics/skills                   # Frontend, testing
npx add-skill obra/superpowers                    # TDD, git worktrees
npx add-skill trailofbits/skills                  # Security, semgrep

# 2. Configurar API keys (opcional)
export GITHUB_TOKEN="ghp_..."
export EXA_API_KEY="..."

# 3. Abrir Claude Code e comecar a usar
# Claude ja reconhece tudo automaticamente
```

---

## Fontes

- [skills.sh](https://skills.sh) -- Marketplace de skills
- [add-skill CLI](https://add-skill.org) -- Ferramenta de instalacao
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) -- Documentacao oficial
- [claude-plugins-official](https://github.com/anthropics/claude-plugins-official) -- Plugins oficiais Anthropic