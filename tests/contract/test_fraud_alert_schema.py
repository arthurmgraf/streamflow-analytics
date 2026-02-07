"""Contract tests for FraudAlert schema.

These tests define the schema contract between alert producers (Flink jobs)
and consumers (Airflow DAGs, PostgreSQL Gold layer, Grafana dashboards).

Contract guarantees:
    - FraudAlert always contains required fields
    - fraud_score is bounded [0, 1]
    - rules_triggered contains valid FraudRuleId values
    - Serialization format is stable for Kafka transport
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

import pytest

from src.flink_jobs.common.serialization import (
    deserialize_fraud_alert,
    serialize_fraud_alert,
)
from src.models.fraud_alert import FraudAlert, FraudRuleId

pytestmark = pytest.mark.contract

VALID_RULE_IDS = {"FR-001", "FR-002", "FR-003", "FR-004", "FR-005", "FR-006"}


class TestFraudAlertSchemaContract:
    """Contract: FraudAlert model field requirements."""

    def _make_alert(self) -> FraudAlert:
        return FraudAlert(
            transaction_id="txn-contract-001",
            customer_id="cust-contract-001",
            fraud_score=Decimal("0.85"),
            rules_triggered=[FraudRuleId.HIGH_VALUE, FraudRuleId.VELOCITY],
            rule_details={"FR-001": {"score": 0.9}, "FR-002": {"score": 0.7}},
            transaction_amount=Decimal("1500.00"),
        )

    def test_all_rule_ids_are_valid(self) -> None:
        for rule_id in FraudRuleId:
            assert rule_id.value in VALID_RULE_IDS

    def test_fraud_score_must_be_bounded(self) -> None:
        with pytest.raises(ValueError):
            FraudAlert(
                transaction_id="txn-bad",
                customer_id="cust-bad",
                fraud_score=Decimal("1.5"),
                rules_triggered=[FraudRuleId.HIGH_VALUE],
                transaction_amount=Decimal("100.00"),
            )

    def test_fraud_score_negative_rejected(self) -> None:
        with pytest.raises(ValueError):
            FraudAlert(
                transaction_id="txn-neg",
                customer_id="cust-neg",
                fraud_score=Decimal("-0.1"),
                rules_triggered=[FraudRuleId.HIGH_VALUE],
                transaction_amount=Decimal("100.00"),
            )

    def test_rules_triggered_must_not_be_empty(self) -> None:
        with pytest.raises(ValueError):
            FraudAlert(
                transaction_id="txn-empty",
                customer_id="cust-empty",
                fraud_score=Decimal("0.5"),
                rules_triggered=[],
                transaction_amount=Decimal("100.00"),
            )

    def test_transaction_amount_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            FraudAlert(
                transaction_id="txn-zero",
                customer_id="cust-zero",
                fraud_score=Decimal("0.5"),
                rules_triggered=[FraudRuleId.BLACKLIST],
                transaction_amount=Decimal("0.00"),
            )

    def test_alert_type_default(self) -> None:
        alert = self._make_alert()
        assert alert.alert_type == "fraud_suspected"

    def test_detected_at_auto_set(self) -> None:
        alert = self._make_alert()
        assert isinstance(alert.detected_at, datetime)

    def test_kafka_key_is_customer_id(self) -> None:
        alert = self._make_alert()
        assert alert.to_kafka_key() == "cust-contract-001"

    def test_fraud_score_coercion_from_float(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-coerce",
            customer_id="cust-coerce",
            fraud_score=0.75,  # type: ignore[arg-type]
            rules_triggered=[FraudRuleId.VELOCITY],
            transaction_amount=Decimal("100.00"),
        )
        assert isinstance(alert.fraud_score, Decimal)
        assert alert.fraud_score == Decimal("0.75")

    def test_rule_details_optional(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-no-details",
            customer_id="cust-no-details",
            fraud_score=Decimal("0.5"),
            rules_triggered=[FraudRuleId.BLACKLIST],
            transaction_amount=Decimal("100.00"),
        )
        assert alert.rule_details == {}


class TestFraudAlertSerializationContract:
    """Contract: Serialized FraudAlert format for Kafka."""

    def _make_alert(self) -> FraudAlert:
        return FraudAlert(
            transaction_id="txn-ser-001",
            customer_id="cust-ser-001",
            fraud_score=Decimal("0.85"),
            rules_triggered=[FraudRuleId.HIGH_VALUE],
            rule_details={"FR-001": {"score": 0.9}},
            transaction_amount=Decimal("1500.00"),
        )

    def test_serialized_is_valid_json(self) -> None:
        alert = self._make_alert()
        serialized = serialize_fraud_alert(alert)
        parsed = json.loads(serialized)
        assert isinstance(parsed, dict)

    def test_fraud_score_serialized_as_string(self) -> None:
        alert = self._make_alert()
        serialized = serialize_fraud_alert(alert)
        parsed = json.loads(serialized)
        assert isinstance(parsed["fraud_score"], str)

    def test_roundtrip_preserves_data(self) -> None:
        alert = self._make_alert()
        roundtripped = deserialize_fraud_alert(serialize_fraud_alert(alert))
        assert roundtripped is not None
        assert roundtripped.transaction_id == alert.transaction_id
        assert roundtripped.customer_id == alert.customer_id
        assert roundtripped.fraud_score == alert.fraud_score

    def test_malformed_json_returns_none(self) -> None:
        assert deserialize_fraud_alert("{bad json}") is None

    def test_serialized_contains_required_fields(self) -> None:
        alert = self._make_alert()
        parsed = json.loads(serialize_fraud_alert(alert))
        required = {"transaction_id", "customer_id", "fraud_score", "rules_triggered",
                     "transaction_amount", "alert_type", "detected_at"}
        assert required.issubset(parsed.keys())

    def test_rules_triggered_serialized_as_list(self) -> None:
        alert = self._make_alert()
        parsed = json.loads(serialize_fraud_alert(alert))
        assert isinstance(parsed["rules_triggered"], list)
        assert all(r in VALID_RULE_IDS for r in parsed["rules_triggered"])
