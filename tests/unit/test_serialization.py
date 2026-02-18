"""Unit tests for Kafka SerDe utilities."""

from __future__ import annotations

import json

from src.flink_jobs.common.serialization import (
    deserialize_fraud_alert,
    deserialize_transaction,
    serialize_fraud_alert,
    serialize_transaction,
)
from src.models.fraud_alert import FraudAlert, FraudRuleId
from src.models.transaction import Transaction


class TestTransactionSerde:
    """Tests for Transaction serialization/deserialization."""

    def test_deserialize_valid_json(self) -> None:
        raw = json.dumps(
            {
                "transaction_id": "txn-001",
                "customer_id": "cust-001",
                "store_id": "store-001",
                "amount": "100.50",
                "timestamp": "2026-01-15T10:00:00",
            }
        )
        txn = deserialize_transaction(raw)
        assert txn is not None
        assert txn.transaction_id == "txn-001"

    def test_deserialize_invalid_json(self) -> None:
        result = deserialize_transaction("not-json{")
        assert result is None

    def test_deserialize_invalid_schema(self) -> None:
        raw = json.dumps({"transaction_id": "", "amount": -5})
        result = deserialize_transaction(raw)
        assert result is None

    def test_serialize_roundtrip(self) -> None:
        txn = Transaction(
            transaction_id="txn-002",
            customer_id="cust-001",
            store_id="store-001",
            amount="200.00",
            timestamp="2026-01-15T10:00:00",
        )
        serialized = serialize_transaction(txn)
        deserialized = deserialize_transaction(serialized)
        assert deserialized is not None
        assert deserialized.transaction_id == "txn-002"


class TestFraudAlertSerde:
    """Tests for FraudAlert serialization/deserialization."""

    def test_serialize_fraud_alert(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-001",
            customer_id="cust-001",
            fraud_score=0.85,
            rules_triggered=[FraudRuleId.HIGH_VALUE],
            transaction_amount=5000,
        )
        serialized = serialize_fraud_alert(alert)
        data = json.loads(serialized)
        assert data["fraud_score"] == "0.85"
        assert data["transaction_id"] == "txn-001"

    def test_deserialize_invalid_json(self) -> None:
        result = deserialize_fraud_alert("broken{")
        assert result is None
