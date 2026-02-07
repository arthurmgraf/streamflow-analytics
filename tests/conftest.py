"""Root-level test configuration and shared fixtures."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from src.flink_jobs.common.state import CustomerFraudState, GeoLocation


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


@pytest.fixture()
def fresh_customer_state() -> CustomerFraudState:
    """Fresh customer state with no history."""
    return CustomerFraudState()


@pytest.fixture()
def warm_customer_state() -> CustomerFraudState:
    """Customer state with 10 transactions of history."""
    state = CustomerFraudState()
    now = time.time()
    for i in range(10):
        state.amount_stats.update(100.0 + i * 5)
        state.hour_stats.update(14.0 + (i % 3))
        state.velocity_window.add(now + i * 600)
    state.last_location = GeoLocation(
        latitude=-23.5505, longitude=-46.6333, timestamp_epoch=now + 5400,
    )
    return state


@pytest.fixture()
def blacklisted_customer_state() -> CustomerFraudState:
    """Customer state flagged as blacklisted with history."""
    state = CustomerFraudState(blacklisted=True)
    now = time.time()
    for i in range(5):
        state.amount_stats.update(200.0)
        state.velocity_window.add(now + i * 300)
    return state


@pytest.fixture()
def high_velocity_state() -> CustomerFraudState:
    """Customer state with many recent transactions (velocity trigger)."""
    state = CustomerFraudState()
    now = time.time()
    for i in range(20):
        state.amount_stats.update(50.0)
        state.hour_stats.update(12.0)
        state.velocity_window.add(now + i * 10)
    return state


@pytest.fixture(scope="session")
def sample_feature_vector() -> list[float]:
    """Sample ML feature vector (6 dimensions)."""
    return [2.5, 8.0, 1.5, 500.0, 0.0, 3.2]
