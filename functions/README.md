# Cloud Functions

> Serverless event-driven functions

---

## Structure

```text
functions/
├── README.md                  # This file
│
├── src/
│   ├── functions/             # Individual cloud functions
│   │   └── {{function_name}}/ # One folder per function
│   │       ├── __init__.py
│   │       └── main.py        # Entry point
│   │
│   └── shared/                # Shared utilities across functions
│       ├── adapters/          # External service adapters
│       │   └── .gitkeep       # e.g., storage.py, messaging.py, database.py
│       ├── schemas/           # Pydantic/data models
│       │   └── .gitkeep       # e.g., messages.py, entities.py
│       └── utils/             # Utilities
│           └── .gitkeep       # e.g., logging.py, config.py
│
├── tests/
│   ├── unit/                  # Unit tests for functions
│   ├── integration/           # Integration tests
│   └── fixtures/              # Test fixtures/data
│
├── deploy/                    # Deployment configurations
│   └── .gitkeep               # e.g., Dockerfiles, deploy scripts
│
└── scripts/                   # Helper scripts
    └── .gitkeep               # e.g., local dev, seed data
```

---

## Function Pattern

Each function follows a consistent pattern:

```python
# functions/src/functions/{{function_name}}/main.py

import functions_framework  # or your framework

@functions_framework.cloud_event
def handler(event):
    """{{Function description}}."""
    # 1. Parse event
    # 2. Process data
    # 3. Emit result
    pass
```

---

## Shared Adapters

Use the adapter pattern for external services:

| Adapter | Purpose | Example |
|---------|---------|---------|
| `storage.py` | File/object storage operations | GCS, S3, Azure Blob |
| `messaging.py` | Event messaging | Pub/Sub, SQS, Kafka |
| `database.py` | Database operations | BigQuery, DynamoDB, PostgreSQL |
| `llm.py` | LLM provider abstraction | OpenAI, Gemini, Anthropic |

---

## Adding a New Function

1. Create the function directory:

```bash
mkdir -p functions/src/functions/{{new_function}}/
touch functions/src/functions/{{new_function}}/__init__.py
touch functions/src/functions/{{new_function}}/main.py
```

2. Implement the handler following the pattern above
3. Add tests in `functions/tests/unit/test_{{new_function}}.py`
4. Add deployment config if needed
