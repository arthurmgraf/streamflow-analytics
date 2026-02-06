# Code Generation & Synthetic Data

> Tools for generating test data, synthetic samples, and code artifacts

---

## Structure

```text
gen/
├── README.md              # This file
│
├── assets/                # Static assets (fonts, icons, logos, images)
│   └── .gitkeep
│
├── samples/               # Generated sample outputs
│   └── .gitkeep
│
├── src/                   # Generator source code
│   └── .gitkeep           # e.g., generator modules, schemas
│
├── templates/             # Generation templates
│   └── .gitkeep           # e.g., document templates, layouts
│
└── tests/                 # Generator tests
    └── .gitkeep
```

---

## Purpose

This directory contains tools for generating:

- **Synthetic test data** - Realistic fake data for testing pipelines
- **Sample documents** - Documents, images, or files for development
- **Code scaffolds** - Auto-generated boilerplate code
- **Fixtures** - Test fixtures and mock data

---

## Usage

```bash
# Example: generate synthetic data
python -m gen.src.{{generator}} --count 10 --output gen/samples/

# Example: generate test fixtures
python -m gen.src.{{generator}} --type fixtures --output tests/fixtures/
```

---

## Guidelines

- Keep generators separate from main application code
- Store generated samples in `samples/` (gitignored if large)
- Use templates for consistent output formatting
- Test generators to ensure output validity
