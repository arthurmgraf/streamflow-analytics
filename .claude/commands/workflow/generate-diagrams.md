# Generate Diagrams Command

> Automated generation of professional Excalidraw diagrams from project analysis

## Usage

```bash
/generate-diagrams
/generate-diagrams architecture
/generate-diagrams data-flow agents
/generate-diagrams --style minimal
/generate-diagrams --output custom/path
```

---

## Overview

The `/generate-diagrams` command analyzes your project structure, code, and configurations to automatically generate clean, professional Excalidraw diagrams suitable for:

- 📊 **Presentations** - Portfolio showcases and client demos
- 📚 **Documentation** - Technical architecture guides
- 💼 **Sales** - Proposal visuals and pitch decks
- 🎓 **Education** - Training materials and workshops

**Key Features:**
- ✅ Intelligent project analysis
- ✅ Multiple diagram types (architecture, data flow, AI agents, ERD)
- ✅ Clean, minimalist, didactic visual style
- ✅ Technology logos and icons
- ✅ Reusable across any project type

---

## Command Syntax

### Basic Usage

```bash
/generate-diagrams
```

Generates **all relevant diagram types** for the current project:
- Complete mega-diagram (all-in-one)
- Architecture / infrastructure diagram
- Data flow / pipeline diagram (if applicable)
- Multi-agent orchestration (if applicable)
- Data model / star schema (if applicable)

**Output:** `diagrams/generated/`

---

### Generate Specific Types

```bash
/generate-diagrams architecture
```

Generate only the **architecture diagram**.

```bash
/generate-diagrams data-flow agents
```

Generate **data flow** and **AI agents** diagrams only.

**Available types:**
- `architecture` - Infrastructure and system architecture
- `data-flow` - Data pipeline and medallion layers
- `agents` - Multi-agent orchestration and MCP
- `data-model` - Star schema and ERD
- `pipeline` - Pipeline execution order and dependencies
- `complete` - All-in-one mega diagram (default)

---

### Options

#### Style

```bash
/generate-diagrams --style minimal
```

- `complete` (default) - Full visual polish with icons, colors, annotations
- `minimal` - Simplified version with basic shapes and labels

#### Custom Output Path

```bash
/generate-diagrams --output docs/diagrams
```

Specify custom output directory (default: `diagrams/generated/`)

#### Force Regenerate

```bash
/generate-diagrams --force
```

Regenerate all diagrams even if they already exist (overwrites existing files).

---

## What Gets Generated

### Project Type Detection

The command analyzes your project and generates appropriate diagrams:

| Project Type | Diagrams Generated |
|--------------|-------------------|
| **GCP Data Platform** | Architecture, Medallion Pipeline, Star Schema |
| **Multi-Agent AI** | Architecture, Agent Orchestration, MCP Integration |
| **Web Application** | System Architecture, Microservices, API Flow |
| **Data Engineering** | Pipeline Execution, Data Lineage, Transformations |
| **Event-Driven** | Event Flow, Message Queue Architecture |

### Output Structure

```
diagrams/generated/
├── complete.excalidraw                    # All-in-one mega diagram
├── architecture/
│   └── infrastructure.excalidraw          # Cloud services, infrastructure
├── data-flow/
│   ├── medallion-pipeline.excalidraw      # Bronze → Silver → Gold
│   └── pipeline-execution.excalidraw      # Script execution order
├── agents/
│   ├── multi-agent-orchestration.excalidraw  # Agent interactions
│   └── mcp-integration.excalidraw         # Model Context Protocol
└── data-model/
    └── star-schema.excalidraw             # Dimensional model
```

---

## How It Works

### Phase 1: Analysis (10-20 seconds)

```
Analyzing project structure...
Scanning: cloud_functions/, sql/, scripts/, config/
Detected: Python, BigQuery, Cloud Storage, Cloud Functions
Pattern: Event-driven pipeline + Medallion architecture
```

The agent:
- Scans directory structure
- Reads configuration files
- Analyzes code imports and dependencies
- Identifies technologies (GCP, AWS, databases, AI frameworks)
- Detects architectural patterns

### Phase 2: Planning (5-10 seconds)

```
Planning diagrams...
- Infrastructure (4 zones: On-Prem, GCP, AI, Business)
- Medallion Pipeline (vertical flow: Bronze→Silver→Gold)
- Star Schema (fact_sales + 4 dimensions)
```

The agent:
- Decides which diagram types are relevant
- Selects layout templates (horizontal zones, vertical flow, hub-spoke)
- Maps technologies to visual components
- Plans color coding and spacing

### Phase 3: Generation (20-40 seconds)

```
Generating diagrams...
✓ complete.excalidraw (2100×2000px, 3 sections, 120 elements)
✓ architecture/infrastructure.excalidraw (2100×750px, 4 zones)
✓ data-flow/medallion-pipeline.excalidraw (1200×1500px)
✓ data-model/star-schema.excalidraw (1000×800px)
```

The agent:
- Generates Excalidraw JSON for each diagram
- Applies colors, fonts, spacing from style guide
- Adds technology icons and labels
- Validates JSON structure
- Writes files to output directory

---

## Examples

### Example 1: Full Generation

```bash
/generate-diagrams
```

**Output:**
```
✅ Generated 5 diagrams in diagrams/generated/

Diagrams created:
- complete.excalidraw (2100×2000px, 3 sections, 120 elements)
- architecture/infrastructure.excalidraw (2100×750px, 4 zones, 45 elements)
- data-flow/medallion-pipeline.excalidraw (1200×1500px, 35 elements)
- agents/multi-agent-orchestration.excalidraw (1400×900px, 25 elements)
- data-model/star-schema.excalidraw (1000×800px, 15 elements)

Technologies detected:
- GCP: Cloud Storage, BigQuery, Cloud Functions
- Python: pandas, numpy, google-cloud-bigquery
- Database: PostgreSQL
- AI: Multi-agent orchestration, MCP

Patterns identified:
- Medallion Architecture (Bronze/Silver/Gold)
- Event-Driven Pipeline (GCS trigger → Cloud Function)
- Multi-Agent System (Orchestrator + 3 agents)
- Star Schema (1 fact, 4 dimensions)

Next steps:
1. Open diagrams in Excalidraw: https://excalidraw.com
2. Customize as needed (colors, labels, positioning)
3. Export to PNG/SVG for presentations
```

---

### Example 2: Architecture Only

```bash
/generate-diagrams architecture
```

**Output:**
```
✅ Generated 1 diagram

- architecture/infrastructure.excalidraw (2100×750px, 4 zones)
  Zones: On-Premise, GCP Cloud, Agentic AI, Business Value
  Components: 12 services, 8 data flows, 3 integrations
```

---

### Example 3: Custom Output

```bash
/generate-diagrams --output docs/diagrams/v2 --force
```

**Output:**
```
✅ Generated 5 diagrams in docs/diagrams/v2/
(Overwrote existing files)
```

---

## Visual Style

All generated diagrams follow a **clean, minimalist, didactic** style:

### Colors
- **On-Premise:** Gray (`#4a5568` / `#f8f9fa`)
- **GCP Cloud:** Blue (`#4285f4` / `#e8f0fe`)
- **Agentic AI:** Purple (`#7c3aed` / `#f3e8ff`)
- **Business:** Red (`#ef4444` / `#fee2e2`)
- **Bronze:** Orange (`#e65100` / `#f9ab00`)
- **Silver:** Gray (`#616161` / `#c0c0c0`)
- **Gold:** Gold (`#f57f17` / `#ffd700`)

### Layout
- **Generous whitespace** - Minimum 40px between elements
- **Grid-aligned** - All coordinates in multiples of 10px
- **Hierarchical zones** - Background containers for grouping
- **Clear labels** - 16-18px readable text on all components

### Icons
- **Text-based icons** - `☁ GCS`, `📊 BQ`, `⚡ CF`, `🤖 AI`
- **Technology recognition** - Standard emojis for quick identification
- **Consistent placement** - Top-center or left-aligned

---

## Integration with Workflows

### Automatic Generation

The command can be automatically triggered by workflow hooks:

**On `/ship` completion:**
```yaml
post_ship_hooks:
  - name: update_diagrams
    command: /generate-diagrams
    condition: code_changed
```

**On `/build` completion:**
```yaml
post_build_hooks:
  - name: generate_diagrams
    command: /generate-diagrams architecture data-flow
    condition: major_milestone
```

This ensures diagrams stay current with code changes.

---

## Customization

### Editing Generated Diagrams

1. **Open in Excalidraw:**
   - Go to https://excalidraw.com
   - File → Open → Select `.excalidraw` file

2. **Customize:**
   - Adjust colors, sizes, positions
   - Add/remove elements
   - Change labels and text
   - Add custom icons or images

3. **Export:**
   - File → Export image → PNG/SVG
   - Use in presentations, docs, portfolio

### Regeneration

If you make code changes:
```bash
/generate-diagrams --force
```

This regenerates all diagrams with latest project state.

---

## Troubleshooting

### Issue: No diagrams generated

**Cause:** Project structure not recognized

**Solution:**
- Ensure project has recognizable files (Python, SQL, configs)
- Check `README.md` exists with project description
- Manually specify diagram types: `/generate-diagrams architecture`

---

### Issue: Diagrams look cluttered

**Cause:** Too many components detected

**Solution:**
- Edit diagram in Excalidraw to simplify
- Focus on major components, hide implementation details
- Generate individual diagrams instead of complete

---

### Issue: Missing technologies

**Cause:** Technologies not detected in code scan

**Solution:**
- Add imports/references to code
- Update `README.md` with technology list
- Manually edit diagram to add missing components

---

### Issue: JSON validation error

**Cause:** Invalid Excalidraw format generated

**Solution:**
- Retry with `--force` flag
- Report issue with project details
- Use minimal style: `--style minimal`

---

## Quality Guarantees

All generated diagrams meet these standards:

- ✅ **Valid Excalidraw JSON** - Opens correctly in Excalidraw
- ✅ **No overlapping text** - Minimum 20px clearance
- ✅ **Consistent colors** - Semantic color palette
- ✅ **Proper spacing** - 40-60px between components
- ✅ **Clear labels** - Every component is labeled
- ✅ **Technology icons** - Visual recognition aids
- ✅ **Professional appearance** - Portfolio-ready quality

**Target:** 90%+ accuracy and visual quality

---

## Agent Details

**Agent:** `diagram-generator-agent`
**Location:** `.claude/agents/diagram-generator-agent.md`
**KB Location:** `.claude/kb/diagram-generation/`

**Tools used by agent:**
- Read (code, configs, documentation)
- Glob (file discovery)
- Grep (technology detection)
- Bash (project structure analysis)

---

## Examples Gallery

### GCP Data Platform

**Command:** `/generate-diagrams`

**Generated:**
- 4-zone architecture (On-Prem → GCP → AI → Business)
- Medallion pipeline (Bronze → Silver → Gold)
- Star schema (fact_sales + dimensions)

**Technologies:** GCS, BigQuery, Cloud Functions, Python

---

### Multi-Agent AI System

**Command:** `/generate-diagrams`

**Generated:**
- Hub-and-spoke orchestration
- MCP integration layer
- Knowledge base architecture

**Technologies:** LangChain, OpenAI, Claude, Chroma

---

### Web Application

**Command:** `/generate-diagrams architecture`

**Generated:**
- 3-tier architecture (Frontend → API → Database)
- Microservices layout
- API flow diagram

**Technologies:** React, Node.js, PostgreSQL, Redis

---

## Next Steps After Generation

1. **Review diagrams** - Open in Excalidraw, check accuracy
2. **Customize** - Adjust colors, labels, layout as needed
3. **Export** - Save as PNG/SVG for presentations
4. **Update documentation** - Link diagrams in README.md
5. **Share** - Use in portfolio, proposals, demos

---

## Related Commands

- `/ship` - Ship completed work (can auto-generate diagrams)
- `/build` - Build and test (can auto-generate diagrams)
- `/design` - Design phase (use diagrams for architecture planning)

---

## Tips

💡 **Best Practices:**
- Generate diagrams early in project for documentation
- Regenerate after major architecture changes
- Use complete diagram for comprehensive view
- Use individual diagrams for focused presentations
- Export to PNG for inclusion in slides/docs

💡 **Performance:**
- First generation: 30-60 seconds (full analysis)
- Subsequent: 20-30 seconds (cached structure)
- Individual types: 10-20 seconds each

💡 **Quality:**
- Review generated diagrams for accuracy
- Customize in Excalidraw as needed
- Provide feedback to improve detection

---

## Support

**Knowledge Base:** `.claude/kb/diagram-generation/`
**Agent Documentation:** `.claude/agents/diagram-generator-agent.md`
**Examples:** `diagrams/alt2_handcrafted.excalidraw`

For issues or improvements, update the KB or agent configuration.

---

**Last Updated:** 2026-01-30
**Version:** 1.0
**Status:** Production-ready for MVP
