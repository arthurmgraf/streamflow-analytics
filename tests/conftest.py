"""Root-level test configuration and shared fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def config_dir() -> Path:
    """Path to test config directory."""
    return Path(__file__).resolve().parent.parent / "config"


@pytest.fixture(scope="session")
def sample_transaction_data() -> dict[str, object]:
    """Valid transaction data for tests."""
    return {
        "transaction_id": "txn-001",
        "customer_id": "cust-001",
        "store_id": "store-001",
        "amount": "150.50",
        "currency": "BRL",
        "timestamp": "2026-01-15T10:30:00",
    }


@pytest.fixture(scope="session")
def sample_customer_data() -> dict[str, object]:
    """Valid customer data for tests."""
    return {
        "customer_id": "cust-001",
        "name": "Maria Silva",
        "email": "maria@example.com",
        "city": "São Paulo",
        "state": "SP",
    }


@pytest.fixture(scope="session")
def sample_store_data() -> dict[str, object]:
    """Valid store data for tests."""
    return {
        "store_id": "store-001",
        "name": "Loja Centro",
        "city": "São Paulo",
        "state": "SP",
        "latitude": -23.5505,
        "longitude": -46.6333,
    }
