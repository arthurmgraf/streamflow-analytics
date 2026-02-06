# Guia Completo: Diretorio `.claude/`

> Tudo que voce precisa saber para usar o Claude Code no seu projeto.

---

## Indice

1. [O que e o `.claude/`](#1-o-que-e-o-claude)
2. [Estrutura de Arquivos](#2-estrutura-de-arquivos)
3. [Configuracao (`settings.json` e `settings.local.json`)](#3-configuracao)
4. [MCP Servers (Exa, Context7, GitHub)](#4-mcp-servers)
5. [Knowledge Base (KB)](#5-knowledge-base-kb)
6. [Agents (Agentes Customizados)](#6-agents)
7. [Commands (Comandos Customizados)](#7-commands)
8. [Rules (Regras Modulares)](#8-rules)
9. [Memory (CLAUDE.md)](#9-memory-claudemd)
10. [GitHub Integration (PRs Automaticos)](#10-github-integration)
11. [Permissoes e Seguranca](#11-permissoes-e-seguranca)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. O que e o `.claude/`

O diretorio `.claude/` e a pasta de configuracao do **Claude Code** no nivel do projeto. Ele contem tudo que o Claude precisa para entender seu projeto, seguir suas regras e usar ferramentas externas.

### Hierarquia de configuracao (do mais global ao mais local)

```
~/.claude/                          # Global (usuario) - vale para TODOS os projetos
  settings.json                     # Config global
  CLAUDE.md                         # Memoria global

seu-projeto/
  .claude/                          # Projeto (equipe) - commitado no git
    settings.json                   # Config compartilhada
    settings.local.json             # Config pessoal (auto-gitignored)
    CLAUDE.md                       # Memoria do projeto
    agents/                         # Agentes customizados
    commands/                       # Comandos customizados
    rules/                          # Regras modulares
    kb/                             # Knowledge Base (consumido pelos agentes)
    notes/                          # Notas de reunioes e planejamento
  .mcp.json                        # MCP servers do projeto (commitado)
  CLAUDE.md                         # Alternativa: memoria na raiz
  CLAUDE.local.md                   # Memoria pessoal (gitignored)
```

### Precedencia (quem ganha)

| Prioridade | Escopo | Arquivo |
|-----------|--------|---------|
| 1 (maior) | Local pessoal | `.claude/settings.local.json` |
| 2 | Projeto | `.claude/settings.json` |
| 3 | Usuario global | `~/.claude/settings.json` |
| 4 (menor) | Managed (empresa) | Sistema |

---

## 2. Estrutura de Arquivos

```
.claude/
├── settings.json               # Configuracoes compartilhadas (git)
├── settings.local.json         # Suas configuracoes pessoais (gitignored)
├── CLAUDE.md                   # Memoria/instrucoes do projeto
├── GUIA-COMPLETO.md            # Este guia
├── README.md                   # README do projeto
│
├── agents/                     # 40 agentes especializados
│   ├── ai-data-engineer.md
│   ├── extraction-specialist.md
│   ├── pipeline-architect.md
│   └── ... (40 arquivos .md)
│
├── commands/                   # 12 comandos customizados
│   ├── core/
│   │   ├── memory.md
│   │   └── sync-context.md
│   ├── workflow/
│   │   ├── brainstorm.md
│   │   ├── build.md
│   │   ├── design.md
│   │   ├── iterate.md
│   │   └── ship.md
│   └── ...
│
├── kb/                         # Knowledge Base (8 dominios, 97 arquivos)
│   ├── _index.yaml             # Indice mestre
│   ├── _templates/             # Templates para novos dominios
│   ├── pydantic/
│   ├── gcp/
│   ├── gemini/
│   ├── langfuse/
│   ├── terraform/
│   ├── terragrunt/
│   ├── crewai/
│   └── openrouter/
│
├── notes/                      # Notas de reunioes
│   ├── 01-business-kickoff.md
│   ├── 02-technical-architecture.md
│   ├── ...
│   └── tasks/                  # Planejamento de tarefas
│
└── rules/                      # Regras modulares (opcional, para criar)
    └── (criar conforme necessario)
```

---

## 3. Configuracao

### Onde o `settings.local.json` funciona?

**Funciona em TODOS os ambientes do Claude Code:**

| Ambiente | Funciona? | Como? |
|----------|-----------|-------|
| **Terminal (CLI)** | Sim | `claude` na pasta do projeto |
| **VSCode Extension** | Sim | Abre o projeto no VSCode, o Claude Code le automaticamente |
| **claude.ai (web)** | Nao | O web app nao le arquivos locais |

O `settings.local.json` e carregado automaticamente quando o Claude Code detecta que voce esta dentro do diretorio do projeto. Nao importa se voce abriu pelo terminal ou pelo VSCode - o arquivo e lido nos dois casos.

**Como funciona na pratica:**
1. Voce abre o projeto no VSCode ou navega ate a pasta no terminal
2. Inicia o Claude Code (`claude` no CLI ou via extensao no VSCode)
3. O Claude Code detecta `.claude/settings.local.json` e aplica as permissoes
4. Todas as ferramentas na lista `allow` rodam sem pedir confirmacao
5. O `outputStyle` define o estilo de resposta dos agentes

### `settings.local.json` (seu arquivo pessoal)

Este e o arquivo que controla **suas permissoes e preferencias pessoais**.
Ele ja existe no seu projeto com esta configuracao:

```json
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Write",
      "Edit",
      "MultiEdit",
      "Glob",
      "Grep",
      "LS",
      "Task",
      "TodoRead",
      "TodoWrite",
      "NotebookRead",
      "NotebookEdit",
      "WebFetch",
      "WebSearch",
      "mcp__exa",
      "mcp__upstash-context-7-mcp",
      "mcp__ref-tools-ref-tools-mcp",
      "mcp__magic",
      "mcp__krieg-2065-firecrawl-mcp-server",
      "Skill"
    ],
    "deny": [],
    "defaultMode": "bypassPermissions"
  },
  "outputStyle": "ai-data-engineer"
}
```

### O que cada campo faz

| Campo | Descricao |
|-------|-----------|
| `permissions.allow` | Lista de ferramentas permitidas sem pedir confirmacao |
| `permissions.deny` | Lista de ferramentas bloqueadas |
| `defaultMode` | `bypassPermissions` = nao pede confirmacao para tools permitidas |
| `outputStyle` | Estilo de resposta do agente (ex: `ai-data-engineer`) |

### `settings.json` (compartilhado com equipe)

Mesma estrutura, mas commitado no git. Use para regras da equipe:

```json
{
  "permissions": {
    "allow": ["Read", "Glob", "Grep"],
    "deny": []
  }
}
```

### Diferenca entre os dois

| Arquivo | Visivel no git? | Quem usa? | Onde funciona? |
|---------|----------------|-----------|----------------|
| `settings.json` | Sim | Toda a equipe | CLI + VSCode |
| `settings.local.json` | Nao (gitignored) | So voce | CLI + VSCode |

---

## 4. MCP Servers

### O que sao MCP Servers?

MCP (Model Context Protocol) sao **servidores externos** que dao superpoderes ao Claude Code. Eles permitem:
- Pesquisar na web (Exa)
- Buscar documentacao atualizada (Context7)
- Interagir com GitHub (criar PRs, issues, etc.)
- Scraping de sites (Firecrawl)

### Seus MCPs configurados (status atual)

```
upstash-context7: cmd /c npx -y @upstash/context7-mcp     -> Conectado
exa-mcp-server:   cmd /c npx -y exa-mcp-server             -> Conectado
github:           https://api.githubcopilot.com/mcp/ (HTTP) -> Conectado (com token)
```

### Onde configurar MCP Servers

Existem **3 formas** de configurar MCPs:

#### Forma 1: Via CLI (`claude mcp add`) - Recomendado

```bash
# Adicionar MCP local (so voce, gravado em ~/.claude.json)
claude mcp add-json nome-do-server '{"command":"cmd","args":["/c","npx","-y","pacote"]}'

# Adicionar MCP no projeto (equipe, gravado em .mcp.json)
claude mcp add --transport http nome --scope project https://url

# Listar MCPs configurados
claude mcp list

# Remover MCP
claude mcp remove nome
```

> **IMPORTANTE no Windows**: Sempre use `cmd /c` antes de `npx` nos MCPs stdio.
> Sem isso, o MCP falha com erro de PATH no Windows nativo.

#### Forma 2: Via Smithery (instalador de MCPs)

```bash
# Instalar no terminal INTERATIVO (nao funciona em scripts/automatizado)
npx @smithery/cli@latest install @MrunmayS/exa-mcp-server --client claude
npx @smithery/cli@latest install @upstash/context7-mcp --client claude
```

Smithery e um marketplace de MCPs. Ele configura automaticamente o MCP no Claude Code.
Porem, precisa de terminal interativo (nao funciona dentro do Claude Code).

#### Forma 3: Via Plugin Marketplace do Claude Code

Voce ja tem plugins instalados via marketplace oficial:
- `context7` (plugin pre-instalado)
- `github` (plugin pre-instalado)

Para habilitar/gerenciar: dentro do Claude Code, use `/mcp`.

---

### Exa MCP - Pesquisa web

**O que e**: Exa e um motor de busca otimizado para IA. Permite pesquisar na web,
encontrar codigo e buscar informacoes atualizadas.

**Como esta configurado**:
```json
{"command": "cmd", "args": ["/c", "npx", "-y", "exa-mcp-server"]}
```

**Precisa de API key?**

| Situacao | Funciona? | Detalhes |
|----------|-----------|----------|
| Sem `EXA_API_KEY` | Parcial | O servidor MCP inicia e conecta, mas as buscas podem falhar ou retornar resultados limitados |
| Com `EXA_API_KEY` | Completo | Pesquisa web completa, busca de codigo, resultados ricos |

**Na pratica sem API key**: O MCP aparece como "Connected" no `claude mcp list`
porque o **servidor** inicia corretamente. Porem, quando o Claude tenta fazer uma
pesquisa, o servidor precisa chamar a API da Exa - e ai precisa do token.

**Voce precisa da API key?** Depende:
- Se voce ja tem `WebSearch` na lista de permissoes (e tem!), o Claude Code pode
  pesquisar na web **sem** Exa, usando a ferramenta nativa `WebSearch`
- Exa e um upgrade: resultados mais precisos, busca de codigo, melhor para queries tecnicas
- Se nao quiser pagar por Exa, pode usar so `WebSearch` nativo e funciona bem

**Se quiser usar Exa no futuro**:
1. Crie conta em https://exa.ai (tem free tier)
2. No PowerShell admin:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("EXA_API_KEY", "sua_key", "User")
   ```
3. Reinicie o terminal/VSCode

**Se quiser remover o Exa MCP**:
```bash
claude mcp remove exa-mcp-server
```

---

### Context7 MCP - Documentacao atualizada

**O que e**: Context7 (Upstash) busca documentacao atualizada de qualquer
biblioteca/framework diretamente da fonte oficial. Quando voce pergunta sobre
React 19, Terraform 1.9, ou Pydantic v2, o Context7 busca a doc mais recente.

**Como esta configurado**:
```json
{"command": "cmd", "args": ["/c", "npx", "-y", "@upstash/context7-mcp"]}
```

**Precisa de API key? NAO.**

Context7 e **100% gratuito** e nao precisa de nenhuma API key.
Ele funciona diretamente via npx sem configuracao adicional.

| Situacao | Funciona? |
|----------|-----------|
| Sem API key | Sim, 100% funcional |
| Sem conta | Sim, nao precisa criar conta |
| Sem internet | Nao (precisa buscar docs online) |

**Na pratica**: Quando o Claude precisa consultar documentacao tecnica, ele
usa o Context7 para buscar a versao mais recente. Isso e especialmente util
porque o conhecimento do Claude tem uma data de corte - o Context7 preenche
essa lacuna com docs atualizadas.

**Exemplo de uso**:
```
"Consulte a documentacao mais recente do Terraform provider para GCP"
"Busque no Context7 como configurar Pub/Sub com Cloud Run"
```

Ja existe tambem um plugin pre-instalado em:
`~/.claude/plugins/marketplaces/claude-plugins-official/external_plugins/context7/.mcp.json`

---

### GitHub MCP - PRs e Issues automaticos

**O que e**: O GitHub MCP permite ao Claude Code interagir diretamente com
repositorios GitHub - criar PRs, issues, reviews, listar branches, etc.

**Como esta configurado**:
```json
{
  "type": "http",
  "url": "https://api.githubcopilot.com/mcp/",
  "headers": {
    "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
  }
}
```

**Precisa de token? SIM.**

O GitHub MCP **obrigatoriamente** precisa de um `GITHUB_PERSONAL_ACCESS_TOKEN`.
Sem ele, o MCP nao consegue autenticar com a API do GitHub.

**Como configurar o token permanentemente no Windows**:

```powershell
# PowerShell como ADMINISTRADOR
[System.Environment]::SetEnvironmentVariable(
  "GITHUB_PERSONAL_ACCESS_TOKEN",
  "github_pat_SEU_TOKEN_AQUI",
  "User"
)
```

Depois reinicie o terminal/VSCode para a variavel ser carregada.

**Alternativa: GitHub CLI (`gh`)**

Mesmo sem o MCP, o Claude Code consegue criar PRs usando o `gh` (GitHub CLI):

```bash
# Ja instalado no seu sistema (v2.85.0)
# Falta autenticar:
gh auth login

# Depois disso, o Claude Code pode usar:
# gh pr create, gh issue create, gh pr review, gh pr merge
```

O `gh` CLI e mais simples que o MCP: so precisa de `gh auth login` uma vez
e funciona para sempre. O MCP e mais completo mas precisa do token como
variavel de ambiente.

### Verificar MCPs ativos

```bash
# Ver todos os MCPs configurados e status de conexao
claude mcp list

# Ver detalhes de um MCP especifico
claude mcp get exa-mcp-server

# Remover um MCP
claude mcp remove nome-do-server
```

### Resumo: O que precisa de API key?

| MCP | Precisa de key? | Custo | Alternativa nativa |
|-----|----------------|-------|--------------------|
| **Context7** | Nao | Gratuito | Nenhuma (e unico) |
| **Exa** | Sim (para buscas) | Free tier disponivel | `WebSearch` (nativo do Claude) |
| **GitHub** | Sim (token PAT) | Gratuito | `gh` CLI (GitHub CLI) |

---

## 5. Knowledge Base (KB)

### Como funciona o KB neste projeto

O KB e um **sistema customizado** deste projeto. Nao e uma feature nativa do Claude Code, mas sim uma **convencao** usada pelos agentes customizados.

### Estrutura do KB

```
.claude/kb/
├── _index.yaml              # Registro de todos os dominios
├── _templates/              # Templates para criar novos dominios
│
├── pydantic/                # Dominio: validacao de dados
│   ├── index.md             # Visao geral do dominio
│   ├── quick-reference.md   # Tabela rapida
│   ├── concepts/            # Conceitos (< 150 linhas cada)
│   │   ├── base-model.md
│   │   ├── validators.md
│   │   └── ...
│   ├── patterns/            # Padroes de implementacao (< 200 linhas cada)
│   │   ├── llm-output-validation.md
│   │   └── ...
│   └── specs/               # Schemas YAML/JSON
│       └── ...
│
├── gcp/                     # Google Cloud Platform
├── gemini/                  # Gemini LLM
├── langfuse/                # LLMOps
├── terraform/               # IaC
├── terragrunt/              # Multi-environment
├── crewai/                  # Multi-agent
└── openrouter/              # LLM fallback
```

### Como o Claude Code usa o KB

1. **Agentes leem o KB** - Cada agente em `.claude/agents/` tem um campo `kb_sources` que indica quais dominios do KB ele consulta
2. **Voce referencia o KB** - Ao pedir ajuda, mencione o dominio: "Use o KB de Pydantic para validar o output"
3. **Templates** - Use `_templates/` para criar novos dominios KB

### Como usar o KB na pratica

```
# No Claude Code, ao conversar:

"Consulte o KB de GCP para desenhar a arquitetura do pipeline"
"Use os patterns de Gemini para criar o prompt de extracao"
"Siga o quick-reference de Terraform para criar o modulo"
```

### Criar um novo dominio KB

```bash
# Use o agente kb-architect
# Ele cria a estrutura completa seguindo os templates
```

Ou manualmente copie `_templates/` e preencha:
1. Copie a pasta de template
2. Renomeie para o nome do dominio
3. Preencha `index.md`, `quick-reference.md`
4. Adicione conceitos em `concepts/`
5. Adicione padroes em `patterns/`
6. Registre em `_index.yaml`

### KB vs Rules vs CLAUDE.md - Quando usar cada um?

| Mecanismo | Quando usar | Exemplo |
|-----------|-------------|---------|
| **KB** (`.claude/kb/`) | Documentacao tecnica detalhada que agentes consultam | Padroes de Terraform, schemas Pydantic |
| **Rules** (`.claude/rules/`) | Regras curtas e diretas que o Claude segue automaticamente | "Use Python 3.11", "Sempre use type hints" |
| **CLAUDE.md** | Instrucoes gerais do projeto | "Este projeto usa GCP", "Siga conventional commits" |

---

## 6. Agents

### O que sao agentes?

Agentes sao **sub-processos especializados** do Claude Code. Cada um tem:
- Ferramentas especificas
- Fontes de conhecimento (KB)
- Personalidade/expertise definida

### Como usar agentes

Agentes sao invocados automaticamente pelo Claude Code quando voce usa o `Task` tool, ou quando o contexto da conversa corresponde a especialidade do agente.

Os 40 agentes estao definidos em `.claude/agents/*.md`.

### Categorias de agentes

| Categoria | Agentes | Uso |
|-----------|---------|-----|
| **AI/ML** | ai-data-engineer, llm-specialist, genai-architect, ai-prompt-specialist | Desenvolvimento com LLMs |
| **Data Engineering** | medallion-architect, spark-specialist, lakeflow-* | Pipelines de dados |
| **Cloud/Infra** | aws-deployer, infra-deployer, ci-cd-specialist | Deploy e infraestrutura |
| **Code Quality** | code-reviewer, code-cleaner, test-generator, python-developer | Qualidade de codigo |
| **Domain** | extraction-specialist, pipeline-architect, function-developer | Especificos deste projeto |
| **Workflow** | brainstorm, define, design, build, iterate, ship | Ciclo de desenvolvimento |
| **Exploracao** | codebase-explorer, kb-architect | Explorar e documentar |
| **Comunicacao** | the-planner, adaptive-explainer, meeting-analyst | Planejamento e comunicacao |

### Exemplo de uso

```
# Claude Code automaticamente escolhe o agente certo baseado no contexto
# Ou voce pode direcionar:

"Use o extraction-specialist para criar o prompt de extracao de invoices"
"Use o pipeline-architect para desenhar a arquitetura event-driven"
"Use o test-generator para criar testes do parser"
```

---

## 7. Commands

### O que sao commands?

Commands sao **atalhos** para tarefas frequentes. Funcionam como slash commands.

### Commands disponiveis

| Comando | O que faz |
|---------|-----------|
| `/workflow brainstorm` | Brainstorm de ideias para features |
| `/workflow build` | Construir/implementar codigo |
| `/workflow design` | Design de arquitetura |
| `/workflow iterate` | Iterar sobre implementacao existente |
| `/workflow ship` | Preparar para deploy |
| `/workflow create-pr` | Criar Pull Request |
| `/workflow define` | Definir requisitos |
| `/review review` | Code review |
| `/knowledge create-kb` | Criar novo dominio KB |
| `/core memory` | Salvar insight na memoria |
| `/core sync-context` | Sincronizar contexto do projeto |
| `/dev dev` | Modo de desenvolvimento |

### Como usar

No Claude Code CLI ou VSCode:
```
/workflow brainstorm
/review review
/knowledge create-kb
```

---

## 8. Rules

### O que sao Rules?

Rules sao **instrucoes modulares** que o Claude Code segue automaticamente.
Ficam em `.claude/rules/*.md` e podem ser condicionais por caminho de arquivo.

### Exemplo de rule

Crie `.claude/rules/python-style.md`:

```markdown
---
paths:
  - "**/*.py"
---

# Estilo Python

- Sempre use type hints
- Use dataclasses para DTOs
- Docstrings em formato Google
- Imports absolutos, nunca relativos
```

### Rule condicional por caminho

```markdown
---
paths:
  - "infrastructure/**/*.tf"
  - "infrastructure/**/*.hcl"
---

# Regras de Terraform

- Sempre use modulos reutilizaveis
- Nomeie recursos com prefixo do ambiente
- Outputs devem ter description
```

A rule so e aplicada quando o Claude esta trabalhando em arquivos que correspondem ao glob pattern.

---

## 9. Memory (CLAUDE.md)

### O que e CLAUDE.md?

E o arquivo de **memoria principal** do projeto. O Claude Code le automaticamente no inicio de cada sessao.

### Onde colocar

| Localizacao | Escopo |
|-------------|--------|
| `./CLAUDE.md` (raiz) | Projeto inteiro |
| `./.claude/CLAUDE.md` | Projeto inteiro (alternativa) |
| `~/.claude/CLAUDE.md` | Todos os seus projetos |
| `./CLAUDE.local.md` | So voce, neste projeto (gitignored) |

### O que incluir

```markdown
# Projeto MR. HEALTH

## Contexto
- Pipeline de processamento de invoices usando GCP
- LLM: Gemini 2.0 Flash com fallback OpenRouter
- Validacao: Pydantic
- Observabilidade: LangFuse

## Convencoes
- Python 3.11
- Type hints obrigatorios
- Conventional commits (feat:, fix:, docs:)
- Terraform com Terragrunt para multi-env

## Arquitetura
- Cloud Run functions (serverless)
- Pub/Sub (mensageria)
- GCS (storage)
- BigQuery (warehouse)

## Links
- @.claude/notes/summary-requirements.md
- @.claude/kb/_index.yaml
```

### Imports com @

Voce pode importar outros arquivos usando `@`:

```markdown
Veja os requisitos em @.claude/notes/summary-requirements.md
Consulte o KB em @.claude/kb/_index.yaml
```

---

## 10. GitHub Integration

### Como o Claude Code faz PRs automaticos

Existem **3 formas** de integrar com GitHub:

### Forma 1: GitHub CLI (`gh`) - Mais simples

O Claude Code usa `gh` nativamente:

```bash
# Instalar
winget install GitHub.cli

# Autenticar
gh auth login

# Agora o Claude Code pode fazer:
# - gh pr create
# - gh issue create
# - gh pr review
# - gh pr merge
```

### Forma 2: GitHub MCP Server

Adiciona capacidades extras via MCP:

```bash
# Ja instalado como plugin no seu sistema
# Para ativar, use /mcp dentro do Claude Code

# Ou adicione manualmente:
claude mcp add --transport http github https://api.githubcopilot.com/mcp/
```

Requer `GITHUB_PERSONAL_ACCESS_TOKEN` como variavel de ambiente.

### Forma 3: GitHub Actions com Claude Code

Para automacao completa (Claude cria PRs quando voce dorme):

1. Instale o **Claude Code GitHub App**: https://github.com/apps/claude
2. No repositorio, crie `.github/workflows/claude.yml`:

```yaml
name: Claude Code
on:
  issues:
    types: [labeled]
  issue_comment:
    types: [created]

jobs:
  claude:
    if: |
      (github.event.label.name == 'claude') ||
      (github.event.comment.body == '@claude')
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

3. Adicione `ANTHROPIC_API_KEY` nos secrets do repositorio
4. Agora, qualquer issue com label `claude` ou comentario `@claude` dispara o Claude Code

### Seu repositorio

Seu repo ja esta linkado: `arthurmgraf/case_mrhealth`

Para criar PRs:
```bash
# No Claude Code:
"Crie um PR com as mudancas atuais"

# Ou use o command:
/workflow create-pr
```

---

## 11. Permissoes e Seguranca

### `bypassPermissions` mode

Seu `settings.local.json` usa `"defaultMode": "bypassPermissions"`.
Isso significa que **todas as ferramentas na lista `allow` rodam sem pedir confirmacao**.

### Ferramentas permitidas

| Ferramenta | O que faz |
|-----------|-----------|
| `Bash` | Executar comandos no terminal |
| `Read` | Ler arquivos |
| `Write` | Escrever arquivos |
| `Edit` | Editar arquivos existentes |
| `MultiEdit` | Editar multiplos trechos |
| `Glob` | Buscar arquivos por padrao |
| `Grep` | Buscar conteudo em arquivos |
| `LS` | Listar diretorios |
| `Task` | Lancar sub-agentes |
| `TodoRead/Write` | Gerenciar lista de tarefas |
| `NotebookRead/Edit` | Ler/editar Jupyter notebooks |
| `WebFetch` | Buscar conteudo web |
| `WebSearch` | Pesquisar na web |
| `mcp__exa` | Busca web via Exa |
| `mcp__upstash-context-7-mcp` | Documentacao via Context7 |
| `mcp__ref-tools-ref-tools-mcp` | Ferramentas de referencia |
| `mcp__magic` | Ferramentas magic |
| `mcp__krieg-2065-firecrawl-mcp-server` | Web scraping via Firecrawl |
| `Skill` | Executar skills/commands |

### Cuidados

- `bypassPermissions` da liberdade total. Se preferir mais seguranca, mude para `"defaultMode": "auto"` e remova `Bash` da lista allow.
- **Nunca commite** `settings.local.json` (ele e auto-gitignored)
- Para a equipe, use `settings.json` com permissoes mais restritas

---

## 12. Como Criar Novos KBs

### Passo a passo

**1. Crie a estrutura de pastas:**
```
.claude/kb/novo-dominio/
├── index.md                # Visao geral (max 100 linhas)
├── quick-reference.md      # Tabela rapida (max 100 linhas)
├── concepts/               # Conceitos atomicos (max 150 linhas cada)
│   ├── conceito-1.md
│   └── conceito-2.md
├── patterns/               # Padroes de implementacao (max 200 linhas cada)
│   ├── padrao-1.md
│   └── padrao-2.md
└── specs/                  # Schemas (YAML/JSON, sem limite)
    └── schema.yaml
```

**2. Preencha usando os templates em `.claude/kb/_templates/`:**

- `concept.md.template` - Para cada conceito
- `pattern.md.template` - Para cada padrao
- `domain-manifest.yaml.template` - Para registrar no indice

**3. Registre no indice mestre `.claude/kb/_index.yaml`:**

```yaml
novo-dominio:
  name: Nome do Dominio
  description: O que este dominio cobre
  path: novo-dominio/
  entry_points:
    index: index.md
    quick_reference: quick-reference.md
  concepts:
    - name: conceito-1
      path: concepts/conceito-1.md
      confidence: 0.95
  patterns:
    - name: padrao-1
      path: patterns/padrao-1.md
```

**4. Alternativa automatica: use o comando:**
```
/knowledge create-kb
```
Ou peca ao Claude: "Crie um novo dominio KB para [tecnologia]"

### Regras de tamanho

| Tipo | Limite | Motivo |
|------|--------|--------|
| index.md | 100 linhas | Visao geral rapida |
| quick-reference.md | 100 linhas | Lookup instantaneo |
| concept | 150 linhas | Atomico, um conceito por arquivo |
| pattern | 200 linhas | Codigo + explicacao |
| spec | Sem limite | Machine-readable |

---

## 13. Como Criar Novos Agentes

### Estrutura de um agente

Cada agente e um arquivo `.md` em `.claude/agents/[categoria]/nome.md`.

**Estrutura minima:**
```markdown
---
name: meu-agente
description: |
  Descricao do que o agente faz.
  Use PROACTIVELY quando [condicoes].

  <example>
  Context: Quando o usuario pede X
  user: "Faca X"
  assistant: "Vou usar o meu-agente para fazer X."
  </example>

tools: [Read, Write, Edit, Grep, Glob, Bash, TodoWrite]
color: blue
---

# Meu Agente

> **Identity:** O que esse agente e em uma frase
> **Domain:** Dominio principal de conhecimento

## Capabilities

### Capability 1: Nome
**When:** Condicoes de ativacao
**Process:**
1. Passo 1
2. Passo 2
3. Passo 3
```

**Template completo:** `.claude/agents/_template.md.example`

### Passo a passo

1. Copie o template: `_template.md.example`
2. Renomeie para `categoria/nome-do-agente.md`
3. Preencha o frontmatter YAML (name, description, tools, color)
4. Defina as capabilities
5. Adicione KB sources se relevante

### Categorias disponiveis

```
.claude/agents/
├── ai-ml/           # Agentes de IA/ML
├── aws/             # Agentes AWS
├── code-quality/    # Qualidade de codigo
├── communication/   # Comunicacao e planejamento
├── data-engineering/# Engenharia de dados
├── dev/             # Desenvolvimento
├── domain/          # Especificos do projeto
├── exploration/     # Exploracao de codebase
└── workflow/        # Ciclo de desenvolvimento
```

### Cores disponiveis

`blue`, `green`, `orange`, `purple`, `red`, `yellow`

---

## 14. Como Criar Novas Skills (Commands)

### O que sao skills?

Skills sao **slash commands** customizados. Quando voce digita `/workflow brainstorm`,
esta executando a skill definida em `.claude/commands/workflow/brainstorm.md`.

### Estrutura de uma skill

```markdown
# Nome da Skill

> Descricao curta

## Usage

/nome-da-skill <argumentos>

## Overview

O que esta skill faz, passo a passo.

## Process

### Step 1: ...
### Step 2: ...
### Step 3: ...

## Output

O que a skill produz como resultado.
```

### Criar uma nova skill

1. Crie um arquivo `.md` em `.claude/commands/[categoria]/nome.md`
2. A categoria vira o prefixo: `categoria/` -> `/categoria nome`
3. Defina o processo que a skill executa

**Exemplo: criar `/data validate-csv`:**

```
.claude/commands/data/validate-csv.md
```

```markdown
# Validate CSV

> Valida a estrutura e qualidade de arquivos CSV

## Usage

/data validate-csv <caminho-do-csv>

## Process

1. Le o arquivo CSV
2. Verifica encoding, delimitador, colunas
3. Valida tipos de dados
4. Reporta problemas encontrados

## Output

Relatorio de validacao do CSV.
```

### Skills ja disponiveis

| Slash Command | Arquivo |
|---------------|---------|
| `/workflow brainstorm` | commands/workflow/brainstorm.md |
| `/workflow build` | commands/workflow/build.md |
| `/workflow design` | commands/workflow/design.md |
| `/workflow iterate` | commands/workflow/iterate.md |
| `/workflow ship` | commands/workflow/ship.md |
| `/workflow create-pr` | commands/workflow/create-pr.md |
| `/workflow define` | commands/workflow/define.md |
| `/review review` | commands/review/review.md |
| `/knowledge create-kb` | commands/knowledge/create-kb.md |
| `/core memory` | commands/core/memory.md |
| `/core sync-context` | commands/core/sync-context.md |
| `/dev dev` | commands/dev/dev.md |

---

## 15. Como Trabalhar com Plans e Tasks

### O conceito

Organize o trabalho em **Plans** (planos grandes) com **Tasks** (tarefas menores).
Cada plan e uma pasta, cada task e um arquivo markdown detalhado.

### Estrutura

```
.claude/notes/tasks/
├── plan1_processo_atual/
│   ├── TASK_01_processo_atual.md
│   ├── TASK_02_fontes_dados.md
│   └── TASK_03_gargalos.md
├── plan2_processo_futuro/
│   ├── TASK_01_fluxo_tobe.md
│   └── TASK_02_automacao.md
├── plan3_arquitetura/
│   ├── TASK_01_diagrama_gcp.md
│   └── TASK_02_infra.md
├── plan4_datalake/
│   └── TASK_01_medallion.md
└── plan5_backlog/
    └── TASK_01_sprint1.md
```

### Formato de uma Task

```markdown
# TASK XX - Titulo da Task

## Titulo
Nome descritivo

## Objetivo
O que esta task deve alcançar (1-2 paragrafos)

## Contexto
Background necessario para executar

## Criterios de Aceitacao
1. Criterio mensuravel 1
2. Criterio mensuravel 2
3. ...

## Subtasks
### X.1 - Nome da subtask
- Item de checklist
- Item de checklist

### X.2 - Nome da subtask
- Item de checklist

## Dependencias
- Quais tasks devem ser completadas antes desta
- Quais recursos externos sao necessarios

## Agentes Sugeridos
| Agente | Papel | Justificativa |
|--------|-------|---------------|
| nome-do-agente | O que faz | Por que usar |

## Notas Adicionais
- Observacoes importantes
```

### Como usar Plans + Tasks com o Claude Code

**1. Criar um novo plan:**
```
"Crie um plan6_monitoring com 3 tasks para configurar monitoramento"
```

**2. Executar uma task:**
```
"Execute a TASK_01 do plan1_processo_atual"
```

**3. Usar o workflow completo (5 fases):**
```
/workflow brainstorm "ideia"       # Fase 0: Explorar
/workflow define                    # Fase 1: Definir requisitos
/workflow design                    # Fase 2: Desenhar solucao
/workflow build                     # Fase 3: Implementar
/workflow ship                      # Fase 4: Entregar
```

**4. Usar o Dev Loop (execucao automatica):**
```
/dev tasks/plan1_processo_atual/TASK_01_processo_atual.md
```

O dev-loop-executor processa o arquivo com verificacoes, circuit breakers
e invoca agentes conforme necessario.

### Dicas

- Cada task deve ser **autocontida** - ter contexto suficiente para ser executada
- Use `## Dependencias` para indicar a ordem
- Use `## Agentes Sugeridos` para guiar o Claude
- Mantenha tasks com escopo limitado (1-2 horas de trabalho humano)

---

## 16. Tornando o `.claude/` Portavel (Multi-Projeto)

### O problema

Voce quer usar a mesma estrutura de agentes, commands e KB em varios projetos.

### Solucao: Repositorio Template

**1. Crie um repositorio template no GitHub:**

```bash
# Crie um repo separado com sua configuracao base
mkdir claude-template
cd claude-template
git init

# Copie a estrutura .claude
cp -r /caminho/projeto/.claude ./
# Remova arquivos especificos do projeto (notes, etc.)
rm -rf .claude/notes/
rm .claude/settings.local.json

git add .
git commit -m "Template base do .claude"
git push origin main
```

**2. Em cada novo projeto, copie o template:**

```bash
# Opcao A: Clone como submodulo
git submodule add https://github.com/seu-user/claude-template.git .claude

# Opcao B: Copie manualmente
cp -r ~/claude-template/.claude ./

# Opcao C: Use como template no GitHub
# Marque o repo como "Template" nas settings do GitHub
# E use "Use this template" para criar novos projetos
```

### O que e generico vs especifico

| Componente | Portavel? | Onde fica? |
|-----------|-----------|-----------|
| **agents/** | Sim | Template (compartilhado) |
| **commands/** | Sim | Template (compartilhado) |
| **kb/** (dominios genericos) | Sim | Template (Pydantic, Terraform, etc.) |
| **kb/** (dominios do projeto) | Nao | Projeto especifico |
| **notes/** | Nao | Projeto especifico |
| **rules/** | Depende | Genericos no template, especificos no projeto |
| **settings.json** | Sim | Template (permissoes da equipe) |
| **settings.local.json** | Nao | Cada maquina (gitignored) |
| **CLAUDE.md** | Nao | Cada projeto tem o seu |

### Estrutura recomendada do template

```
claude-template/
├── .claude/
│   ├── settings.json              # Permissoes base da equipe
│   ├── agents/                    # Todos os agentes genericos
│   │   ├── _template.md.example
│   │   ├── ai-ml/
│   │   ├── code-quality/
│   │   ├── communication/
│   │   └── workflow/
│   ├── commands/                  # Todos os commands
│   │   ├── core/
│   │   ├── workflow/
│   │   └── review/
│   ├── kb/                        # KBs genericos
│   │   ├── _index.yaml
│   │   ├── _templates/
│   │   ├── pydantic/
│   │   ├── gcp/
│   │   ├── terraform/
│   │   └── terragrunt/
│   └── rules/                     # Rules genericas
│       ├── python-style.md
│       └── git-conventions.md
├── .mcp.json                      # MCPs da equipe
└── README.md
```

### Script de setup para novo projeto

Crie um script `setup-claude.sh`:

```bash
#!/bin/bash
# Configurar .claude em um novo projeto
TEMPLATE_REPO="https://github.com/seu-user/claude-template.git"
TEMP_DIR=$(mktemp -d)

echo "Clonando template..."
git clone --depth 1 "$TEMPLATE_REPO" "$TEMP_DIR"

echo "Copiando .claude/"
cp -r "$TEMP_DIR/.claude" .
rm -rf "$TEMP_DIR"

echo "Criando diretorios do projeto..."
mkdir -p .claude/notes/tasks
mkdir -p .claude/kb  # para KBs especificos do projeto

echo "Pronto! Agora configure:"
echo "1. .claude/settings.local.json (suas permissoes)"
echo "2. CLAUDE.md (contexto do projeto)"
echo "3. .claude/notes/ (reunioes e planejamento)"
```

---

## 17. Troubleshooting

### MCP nao aparece no VSCode

**Causa mais comum no Windows**: O CLI usa path com `c:` minusculo e o VSCode
usa `C:` maiusculo. Isso cria duas entradas separadas em `~/.claude.json`.

**Solucao**: Reconfigure os MCPs pela interface do VSCode ou adicione MCPs
diretamente na interface "Manage MCP Servers" do VSCode.

### MCP nao conecta

```bash
# Verificar MCPs instalados
claude mcp list

# Resetar escolhas de projeto
claude mcp reset-project-choices

# Verificar logs
# Os MCPs aparecem como "connected" ou com erro no inicio da sessao
```

### KB nao e consultado

- Verifique se o agente tem `kb_sources` apontando para o dominio correto
- Mencione explicitamente: "Consulte o KB de [dominio]"
- O KB e lido pelos agentes, nao diretamente pelo Claude Code base

### Permissoes pedindo confirmacao

- Verifique se a ferramenta esta na lista `allow` do `settings.local.json`
- Certifique-se que `defaultMode` esta como `bypassPermissions`

### GitHub nao cria PRs

1. Verifique se `gh` esta instalado: `gh --version`
2. Verifique autenticacao: `gh auth status`
3. Verifique se o repo tem remote: `git remote -v`
4. Se usar MCP, verifique `GITHUB_PERSONAL_ACCESS_TOKEN`

### Windows: MCP com npx falha

No Windows nativo, prefixe com `cmd /c`:
```bash
claude mcp add-json context7 '{"command":"cmd","args":["/c","npx","-y","@upstash/context7-mcp"]}'
```

---

## Resumo Rapido

| Preciso de... | Use... |
|---------------|--------|
| Configurar permissoes | `.claude/settings.local.json` |
| Adicionar instrucoes ao Claude | `CLAUDE.md` ou `.claude/rules/` |
| Consultar documentacao tecnica | `.claude/kb/[dominio]/` |
| Usar agente especializado | `.claude/agents/` (automatico via Task) |
| Executar workflow | `/workflow brainstorm`, `/workflow build`, etc. |
| Conectar ferramenta externa | `claude mcp add` ou `.mcp.json` |
| Criar PR automatico | `gh pr create` ou `/workflow create-pr` |
| Pesquisar na web | Exa MCP ou WebSearch nativo |
| Buscar docs atualizadas | Context7 MCP |
| Criar novo KB | `/knowledge create-kb` ou manual |
| Criar novo agente | Copiar `_template.md.example` |
| Criar nova skill | Arquivo `.md` em `commands/` |
| Organizar trabalho | Plans + Tasks em `notes/tasks/` |
| Reusar em outro projeto | Template repo no GitHub |

---

> Ultima atualizacao: Janeiro 2026.
