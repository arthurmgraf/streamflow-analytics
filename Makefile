.PHONY: help install lint format typecheck test test-cov clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (dev mode)
	pip install -e ".[dev]"

lint: ## Run linter
	ruff check .

format: ## Format code
	ruff format .
	ruff check . --fix

typecheck: ## Run type checker
	mypy src/ --config-file=pyproject.toml

test: ## Run tests
	pytest tests/ -v

test-cov: ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

check: lint typecheck test ## Run all checks (lint + typecheck + test)

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
