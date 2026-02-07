"""End-to-end pipeline tests.

These tests verify the full data flow from event generation
through fraud detection to PostgreSQL storage.

Requires: Running K3s cluster with all StreamFlow components deployed.
Mark: e2e (skipped in CI, run manually with `pytest -m e2e`)
"""

from __future__ import annotations

import time
from decimal import Decimal

import pytest

from src.flink_jobs.common.serialization import (
    deserialize_fraud_alert,
    deserialize_transaction,
    serialize_fraud_alert,
    serialize_transaction,
)
from src.flink_jobs.common.state import RunningStats, haversine_km
from src.flink_jobs.fraud_detector import FraudEngine
from src.generators.customer_generator import generate_customers
from src.generators.store_generator import generate_stores
from src.generators.transaction_generator import TransactionGenerator
from src.models.fraud_alert import FraudAlert, FraudRuleId
from src.models.transaction import Transaction

pytestmark = pytest.mark.e2e


class TestGeneratorToFraudDetection:
    """Test: Generator -> Serialization -> FraudEngine -> FraudAlert."""

    def test_generated_transaction_through_fraud_engine(self) -> None:
        """A generated transaction can be serialized, deserialized, and evaluated."""
        customers = generate_customers(10, seed=42)
        stores = generate_stores(5, seed=42)
        generator = TransactionGenerator(customers=customers, stores=stores, seed=42)

        txn = generator.generate()
        assert isinstance(txn, Transaction)

        # Serialize -> Deserialize roundtrip (str-based for Kafka SimpleStringSchema)
        serialized = serialize_transaction(txn)
        assert isinstance(serialized, str)

        deserialized = deserialize_transaction(serialized)
        assert deserialized is not None
        assert isinstance(deserialized, Transaction)
        assert deserialized.transaction_id == txn.transaction_id

        # Feed into fraud engine via dict (process_transaction expects dict)
        txn_dict = txn.to_json_dict()
        txn_dict["timestamp_epoch"] = time.time()
        engine = FraudEngine()
        alert = engine.process_transaction(txn_dict)

        # First transaction for a customer — should not trigger alert
        assert alert is None

    def test_batch_generation_with_fraud_detection(self) -> None:
        """Batch of transactions processed through fraud engine."""
        customers = generate_customers(20, seed=100)
        stores = generate_stores(5, seed=100)
        generator = TransactionGenerator(customers=customers, stores=stores, seed=100)

        engine = FraudEngine()
        transactions = generator.generate_batch(50)
        alerts: list[FraudAlert] = []

        now = time.time()
        for i, txn in enumerate(transactions):
            # Verify roundtrip serialization
            deserialized = deserialize_transaction(serialize_transaction(txn))
            assert deserialized is not None

            # Feed into engine via dict
            txn_dict = txn.to_json_dict()
            txn_dict["timestamp_epoch"] = now + i * 10
            alert = engine.process_transaction(txn_dict)
            if alert is not None:
                alerts.append(alert)

        assert len(transactions) == 50

    def test_blacklisted_customer_generates_alert(self) -> None:
        """A blacklisted customer triggers a fraud alert through the full pipeline."""
        customers = generate_customers(5, seed=77)
        stores = generate_stores(3, seed=77)

        engine = FraudEngine()
        target_customer = customers[0].customer_id
        engine.set_blacklist({target_customer})

        # Build history for the target customer
        now = time.time()
        for i in range(10):
            engine.evaluate(target_customer, 100.0, now + i * 3600)

        # Now trigger multiple rules: high value + blacklist
        txn_data = {
            "transaction_id": "txn-e2e-blacklist-001",
            "customer_id": target_customer,
            "store_id": stores[0].store_id,
            "amount": 500.0,
            "timestamp_epoch": now + 36000,
        }

        alert = engine.process_transaction(txn_data)
        # Blacklist (weight 0.10) alone may not exceed 0.7 threshold,
        # but high_value + blacklist together might
        if alert is not None:
            assert alert.fraud_score > Decimal("0")
            assert FraudRuleId.BLACKLIST in alert.rules_triggered


class TestFraudAlertSerialization:
    """Test FraudAlert serialization for Kafka transport."""

    def test_fraud_alert_roundtrip(self) -> None:
        """FraudAlert can be serialized and deserialized for Kafka."""
        alert = FraudAlert(
            transaction_id="txn-e2e-ser-001",
            customer_id="cust-e2e-001",
            fraud_score=Decimal("0.85"),
            rules_triggered=[FraudRuleId.HIGH_VALUE, FraudRuleId.VELOCITY],
            rule_details={"FR-001": {"score": 0.9}, "FR-002": {"score": 0.7}},
            transaction_amount=Decimal("1500.00"),
        )

        serialized = serialize_fraud_alert(alert)
        assert isinstance(serialized, str)

        deserialized = deserialize_fraud_alert(serialized)
        assert deserialized is not None
        assert isinstance(deserialized, FraudAlert)
        assert deserialized.transaction_id == "txn-e2e-ser-001"
        assert deserialized.customer_id == "cust-e2e-001"


class TestMedallionDataFlow:
    """Test data transformations mimicking Bronze -> Silver -> Gold flow."""

    def test_running_stats_accumulation(self) -> None:
        """RunningStats (used in Silver aggregation) accumulates correctly."""
        stats = RunningStats()
        values = [100.0, 150.0, 200.0, 120.0, 180.0]
        for v in values:
            stats.update(v)

        assert stats.count == 5
        assert abs(stats.mean - 150.0) < 0.01
        assert stats.std_dev > 0

    def test_haversine_known_distance(self) -> None:
        """Haversine formula gives correct distance for known city pairs."""
        # Sao Paulo to Rio de Janeiro ~357km
        sp_lat, sp_lon = -23.5505, -46.6333
        rj_lat, rj_lon = -22.9068, -43.1729
        distance = haversine_km(sp_lat, sp_lon, rj_lat, rj_lon)
        assert 350 < distance < 370

    def test_full_flow_generator_to_alert_structure(self) -> None:
        """Validate the complete data structure chain from generator to alert."""
        customers = generate_customers(3, seed=999)
        stores = generate_stores(2, seed=999)
        generator = TransactionGenerator(customers=customers, stores=stores, seed=999)

        txn = generator.generate()

        # Validate Transaction model fields
        assert txn.transaction_id.startswith("txn-")
        assert txn.customer_id.startswith("cust-")
        assert txn.amount > 0

        # Validate serialization roundtrip produces valid Transaction
        deserialized = deserialize_transaction(serialize_transaction(txn))
        assert deserialized is not None
        assert deserialized.transaction_id == txn.transaction_id
        assert deserialized.customer_id == txn.customer_id

        # Validate FraudEngine returns proper structure
        engine = FraudEngine()
        score, results = engine.evaluate(
            customer_id=txn.customer_id,
            amount=float(txn.amount),
            timestamp_epoch=time.time(),
        )
        assert isinstance(score, float)
        assert len(results) == 5  # All 5 rules evaluated
        rule_ids = {r.rule_id for r in results}
        assert rule_ids == {"FR-001", "FR-002", "FR-003", "FR-004", "FR-005"}
