# Contributing to StreamFlow Analytics

Thank you for your interest in contributing to StreamFlow Analytics!

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/arthurmgraf/streamflow-analytics.git
   cd streamflow-analytics
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Start infrastructure:
   ```bash
   docker compose up -d  # Kafka, Flink, PostgreSQL
   ```

## Code Standards

- **Linting**: `ruff check src/ tests/`
- **Type checking**: `mypy src/ --strict`
- **Formatting**: `ruff format src/ tests/`
- **Testing**: `pytest tests/ -v`

All code must pass linting, type checking, and tests before merge.

## Testing

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests (requires Docker infrastructure)
pytest tests/integration/ -v -m integration

# Full test suite with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

Minimum coverage threshold: 80%

## Pull Request Process

1. Fork the repository and create a branch from `main`
2. Make your changes with tests
3. Ensure CI passes (lint + type check + tests)
4. Write a clear PR description explaining the "why"
5. Request a review

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation only
- `refactor:` — Code refactoring
- `test:` — Adding or updating tests
- `chore:` — Maintenance tasks
- `infra:` — Infrastructure changes

## Architecture Decision Records

For significant architectural changes, create an ADR in `docs/adr/`. Use the template format:
- Title, Status, Context, Decision, Consequences

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
