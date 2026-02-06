# {{PROJECT_NAME}}

> {{PROJECT_DESCRIPTION}}

---

## Quick Start

```bash
# Clone the repository
git clone {{REPO_URL}}
cd {{PROJECT_ROOT}}

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

---

## Project Structure

```text
{{PROJECT_ROOT}}/
├── src/                   # Main source code
├── tests/                 # Test suites (unit, integration, smoke)
├── functions/             # Cloud functions (serverless)
├── infra/                 # Infrastructure as Code
├── gen/                   # Code generation & synthetic data
├── design/                # Architecture design documents
├── notes/                 # Project meeting notes
├── archive/               # Historical versions
├── .claude/               # Claude Code AI ecosystem
├── pyproject.toml         # Python project configuration
└── README.md              # This file
```

---

## Development

### Prerequisites

- Python 3.11+
- pip or uv

### Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test suite
pytest tests/unit/ -v
pytest tests/integration/ -v
```

### Linting

```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check . --fix
```

---

## Claude Code Ecosystem

This project includes a complete Claude Code `.claude/` ecosystem for AI-assisted development:

| Workflow | Command | Use When |
|----------|---------|----------|
| **Dev Loop** | `/dev "task"` | Quick tasks, prototypes, utilities |
| **SDD Pipeline** | `/brainstorm` → `/define` → `/design` → `/build` → `/ship` | Complex features with traceability |
| **Knowledge Base** | `/create-kb "domain"` | Building domain knowledge for agents |
| **Code Review** | `/review` | AI-powered code review |

See [.claude/README.md](.claude/README.md) for the full ecosystem guide.

---

## Architecture

<!-- Replace with your architecture diagram -->

```text
{{ARCHITECTURE_DIAGRAM}}
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
