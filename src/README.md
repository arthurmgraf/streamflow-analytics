# Source Code

> Main application source code

---

## Structure

```text
src/
├── __init__.py
├── README.md              # This file
│
├── {{MODULE_NAME}}/       # Your main module
│   ├── __init__.py
│   ├── ...                # Module files
│   └── tests/             # Module-specific tests (optional)
│       ├── unit/
│       ├── integration/
│       └── fixtures/
│
└── {{ANOTHER_MODULE}}/    # Additional modules as needed
    └── ...
```

---

## Guidelines

- Each module should have its own `__init__.py`
- Keep modules focused on a single responsibility
- Place module-specific tests alongside the module in `tests/`
- Shared test utilities go in the root `tests/` directory
- Use type hints on all function signatures
- Follow the project's linting and formatting rules
