# Tests

> Project test suites

---

## Structure

```text
tests/
├── README.md              # This file
├── conftest.py            # Shared fixtures
│
├── unit/                  # Unit tests
│   └── .gitkeep           # Fast, isolated, no external deps
│
├── integration/           # Integration tests
│   └── .gitkeep           # Test component interactions
│
└── smoke/                 # End-to-end smoke tests
    ├── stages/            # Pipeline test stages
    ├── validators/        # Result validation
    ├── config/            # Test configuration
    └── fixtures/          # Test data
```

---

## Test Types

| Type | Purpose | Speed | Dependencies |
|------|---------|-------|-------------|
| **Unit** | Test individual functions/classes | Fast | None (mocked) |
| **Integration** | Test component interactions | Medium | Local services |
| **Smoke** | End-to-end pipeline validation | Slow | Full environment |

---

## Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Smoke tests (requires deployed environment)
pytest tests/smoke/ -v

# With coverage
pytest --cov=src --cov-report=term-missing
```

---

## Guidelines

- Unit tests should be fast and isolated (mock external dependencies)
- Integration tests verify component interactions
- Smoke tests validate the full deployed pipeline
- Use fixtures for shared test data
- Follow naming convention: `test_{{module}}_{{function}}.py`
- Aim for meaningful coverage, not just high numbers
