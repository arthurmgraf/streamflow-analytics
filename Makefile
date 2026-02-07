.PHONY: help install lint format typecheck test test-unit test-contract test-integration test-cov check clean deploy deploy-argocd status

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies (dev mode)
	pip install -e ".[dev]"

lint: ## Run linter
	ruff check src/ tests/ scripts/

format: ## Format code
	ruff format src/ tests/ scripts/
	ruff check src/ tests/ scripts/ --fix

typecheck: ## Run type checker (strict)
	mypy src/ scripts/ --strict

test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v --tb=short

test-contract: ## Run contract tests only
	pytest tests/contract/ -v --tb=short

test-integration: ## Run integration tests only
	pytest tests/integration/ -v --tb=short

test-cov: ## Run tests with coverage (fail under 80%)
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=80

check: lint typecheck test ## Run all checks (lint + typecheck + test)

deploy: ## Deploy via kubectl (direct apply)
	bash scripts/deploy.sh all

deploy-argocd: ## Deploy via ArgoCD (GitOps)
	bash scripts/deploy.sh argocd

status: ## Show deployment status
	bash scripts/deploy.sh status

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
