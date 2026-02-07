"""Unit tests for data generators."""

from __future__ import annotations

from decimal import Decimal

from src.generators.customer_generator import generate_customers
from src.generators.fraud_patterns import FraudInjector
from src.generators.store_generator import generate_stores
from src.generators.transaction_generator import TransactionGenerator


class TestCustomerGenerator:
    """Tests for customer generation."""

    def test_generates_correct_count(self) -> None:
        customers = generate_customers(50, seed=42)
        assert len(customers) == 50

    def test_deterministic_with_seed(self) -> None:
        a = generate_customers(10, seed=123)
        b = generate_customers(10, seed=123)
        assert [c.customer_id for c in a] == [c.customer_id for c in b]

    def test_unique_ids(self) -> None:
        customers = generate_customers(100, seed=42)
        ids = [c.customer_id for c in customers]
        assert len(ids) == len(set(ids))

    def test_valid_state_codes(self) -> None:
        customers = generate_customers(20, seed=42)
        for c in customers:
            assert c.state is not None
            assert len(c.state) == 2


class TestStoreGenerator:
    """Tests for store generation."""

    def test_generates_correct_count(self) -> None:
        stores = generate_stores(10, seed=42)
        assert len(stores) == 10

    def test_has_coordinates(self) -> None:
        stores = generate_stores(5, seed=42)
        for s in stores:
            assert s.latitude is not None
            assert s.longitude is not None
            assert -90 <= s.latitude <= 90
            assert -180 <= s.longitude <= 180

    def test_has_category(self) -> None:
        stores = generate_stores(5, seed=42)
        for s in stores:
            assert s.category is not None


class TestTransactionGenerator:
    """Tests for transaction generation."""

    def test_generate_single(self) -> None:
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        gen = TransactionGenerator(customers, stores, seed=42)
        txn = gen.generate()
        assert txn.amount > 0
        assert txn.customer_id.startswith("cust-")
        assert txn.store_id.startswith("store-")

    def test_generate_batch(self) -> None:
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        gen = TransactionGenerator(customers, stores, seed=42)
        batch = gen.generate_batch(100)
        assert len(batch) == 100
        # Timestamps should be increasing
        for i in range(1, len(batch)):
            assert batch[i].timestamp >= batch[i - 1].timestamp

    def test_amount_in_valid_range(self) -> None:
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        gen = TransactionGenerator(customers, stores, seed=42)
        for _ in range(100):
            txn = gen.generate()
            assert txn.amount > 0
            assert txn.amount < Decimal("100000")


class TestFraudInjector:
    """Tests for fraud pattern injection."""

    def test_should_inject_respects_rate(self) -> None:
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        injector = FraudInjector(customers, stores, fraud_rate=0.5, seed=42)
        injections = sum(1 for _ in range(1000) if injector.should_inject())
        # Should be roughly 50% ± 5%
        assert 400 < injections < 600

    def test_inject_modifies_transaction(self) -> None:
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        gen = TransactionGenerator(customers, stores, seed=42)
        injector = FraudInjector(customers, stores, seed=42)
        original = gen.generate()
        modified = injector.inject(original)
        # Something should be different
        assert modified.transaction_id == original.transaction_id  # ID preserved

    def test_generate_fraud_burst(self) -> None:
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        injector = FraudInjector(customers, stores, seed=42)
        burst = injector.generate_fraud_burst("cust-test", count=8)
        assert len(burst) == 8
        # All same customer
        for txn in burst:
            assert txn.customer_id == "cust-test"
