"""Unit tests for Pydantic data models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.models.customer import Customer, RiskProfile
from src.models.fraud_alert import FraudAlert, FraudRuleId
from src.models.store import Store
from src.models.transaction import Transaction


class TestTransaction:
    """Tests for the Transaction model."""

    def test_valid_transaction(self, sample_transaction_data: dict[str, object]) -> None:
        txn = Transaction(**sample_transaction_data)
        assert txn.transaction_id == "txn-001"
        assert txn.amount == Decimal("150.50")
        assert txn.currency == "BRL"

    def test_amount_coercion_from_float(self) -> None:
        txn = Transaction(
            transaction_id="txn-002",
            customer_id="cust-001",
            store_id="store-001",
            amount=99.99,
            timestamp="2026-01-15T10:00:00",
        )
        assert txn.amount == Decimal("99.99")

    def test_amount_coercion_from_int(self) -> None:
        txn = Transaction(
            transaction_id="txn-003",
            customer_id="cust-001",
            store_id="store-001",
            amount=100,
            timestamp="2026-01-15T10:00:00",
        )
        assert txn.amount == Decimal("100")

    def test_amount_must_be_positive(self) -> None:
        with pytest.raises(ValidationError, match="greater than 0"):
            Transaction(
                transaction_id="txn-004",
                customer_id="cust-001",
                store_id="store-001",
                amount=0,
                timestamp="2026-01-15T10:00:00",
            )

    def test_negative_amount_rejected(self) -> None:
        with pytest.raises(ValidationError, match="greater than 0"):
            Transaction(
                transaction_id="txn-005",
                customer_id="cust-001",
                store_id="store-001",
                amount=-50,
                timestamp="2026-01-15T10:00:00",
            )

    def test_empty_transaction_id_rejected(self) -> None:
        with pytest.raises(ValidationError, match="at least 1 character"):
            Transaction(
                transaction_id="",
                customer_id="cust-001",
                store_id="store-001",
                amount=100,
                timestamp="2026-01-15T10:00:00",
            )

    def test_invalid_currency_rejected(self) -> None:
        with pytest.raises(ValidationError, match="pattern"):
            Transaction(
                transaction_id="txn-006",
                customer_id="cust-001",
                store_id="store-001",
                amount=100,
                currency="brl",
                timestamp="2026-01-15T10:00:00",
            )

    def test_latitude_range(self) -> None:
        with pytest.raises(ValidationError, match="less than or equal to 90"):
            Transaction(
                transaction_id="txn-007",
                customer_id="cust-001",
                store_id="store-001",
                amount=100,
                latitude=91.0,
                timestamp="2026-01-15T10:00:00",
            )

    def test_optional_fields_default_none(self) -> None:
        txn = Transaction(
            transaction_id="txn-008",
            customer_id="cust-001",
            store_id="store-001",
            amount=100,
            timestamp="2026-01-15T10:00:00",
        )
        assert txn.product_id is None
        assert txn.payment_method is None
        assert txn.latitude is None
        assert txn.longitude is None

    def test_to_kafka_key(self) -> None:
        txn = Transaction(
            transaction_id="txn-009",
            customer_id="cust-abc",
            store_id="store-001",
            amount=100,
            timestamp="2026-01-15T10:00:00",
        )
        assert txn.to_kafka_key() == "cust-abc"

    def test_to_json_dict(self) -> None:
        txn = Transaction(
            transaction_id="txn-010",
            customer_id="cust-001",
            store_id="store-001",
            amount="250.75",
            timestamp="2026-01-15T10:00:00",
        )
        data = txn.to_json_dict()
        assert data["amount"] == "250.75"
        assert isinstance(data["amount"], str)
        assert data["transaction_id"] == "txn-010"


class TestCustomer:
    """Tests for the Customer model."""

    def test_valid_customer(self, sample_customer_data: dict[str, object]) -> None:
        customer = Customer(**sample_customer_data)
        assert customer.customer_id == "cust-001"
        assert customer.name == "Maria Silva"
        assert customer.risk_profile == RiskProfile.NORMAL

    def test_default_values(self) -> None:
        customer = Customer(customer_id="cust-002", name="João")
        assert customer.avg_transaction_amt == Decimal("0")
        assert customer.total_transactions == 0
        assert customer.risk_profile == RiskProfile.NORMAL

    def test_risk_profiles(self) -> None:
        for profile in RiskProfile:
            customer = Customer(
                customer_id="cust-003",
                name="Test",
                risk_profile=profile,
            )
            assert customer.risk_profile == profile

    def test_empty_name_rejected(self) -> None:
        with pytest.raises(ValidationError, match="at least 1 character"):
            Customer(customer_id="cust-004", name="")

    def test_state_must_be_2_chars(self) -> None:
        with pytest.raises(ValidationError, match="at most 2 character"):
            Customer(customer_id="cust-005", name="Test", state="SPX")

    def test_negative_avg_rejected(self) -> None:
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            Customer(
                customer_id="cust-006",
                name="Test",
                avg_transaction_amt=Decimal("-1"),
            )

    def test_negative_total_transactions_rejected(self) -> None:
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            Customer(customer_id="cust-007", name="Test", total_transactions=-1)


class TestStore:
    """Tests for the Store model."""

    def test_valid_store(self, sample_store_data: dict[str, object]) -> None:
        store = Store(**sample_store_data)
        assert store.store_id == "store-001"
        assert store.name == "Loja Centro"
        assert store.latitude == -23.5505

    def test_state_exactly_2_chars(self) -> None:
        with pytest.raises(ValidationError):
            Store(
                store_id="store-002",
                name="Test",
                city="Rio",
                state="RJX",
            )

    def test_state_too_short(self) -> None:
        with pytest.raises(ValidationError):
            Store(
                store_id="store-003",
                name="Test",
                city="Rio",
                state="R",
            )

    def test_latitude_range(self) -> None:
        with pytest.raises(ValidationError, match="less than or equal to 90"):
            Store(
                store_id="store-004",
                name="Test",
                city="Rio",
                state="RJ",
                latitude=100.0,
            )

    def test_optional_category(self) -> None:
        store = Store(
            store_id="store-005",
            name="Test",
            city="Rio",
            state="RJ",
        )
        assert store.category is None


class TestFraudAlert:
    """Tests for the FraudAlert model."""

    def test_valid_alert(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-001",
            customer_id="cust-001",
            fraud_score=0.85,
            rules_triggered=[FraudRuleId.HIGH_VALUE, FraudRuleId.VELOCITY],
            transaction_amount=5000.00,
        )
        assert alert.fraud_score == Decimal("0.85")
        assert len(alert.rules_triggered) == 2
        assert alert.alert_type == "fraud_suspected"

    def test_fraud_score_range(self) -> None:
        with pytest.raises(ValidationError, match="less than or equal to 1"):
            FraudAlert(
                transaction_id="txn-002",
                customer_id="cust-001",
                fraud_score=1.5,
                rules_triggered=[FraudRuleId.HIGH_VALUE],
                transaction_amount=100,
            )

    def test_fraud_score_negative(self) -> None:
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            FraudAlert(
                transaction_id="txn-003",
                customer_id="cust-001",
                fraud_score=-0.1,
                rules_triggered=[FraudRuleId.HIGH_VALUE],
                transaction_amount=100,
            )

    def test_rules_triggered_not_empty(self) -> None:
        with pytest.raises(ValidationError, match="at least 1 item"):
            FraudAlert(
                transaction_id="txn-004",
                customer_id="cust-001",
                fraud_score=0.8,
                rules_triggered=[],
                transaction_amount=100,
            )

    def test_all_rule_ids(self) -> None:
        assert FraudRuleId.HIGH_VALUE == "FR-001"
        assert FraudRuleId.VELOCITY == "FR-002"
        assert FraudRuleId.GEOGRAPHIC == "FR-003"
        assert FraudRuleId.TIME_ANOMALY == "FR-004"
        assert FraudRuleId.BLACKLIST == "FR-005"

    def test_to_kafka_key(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-005",
            customer_id="cust-abc",
            fraud_score=0.9,
            rules_triggered=[FraudRuleId.BLACKLIST],
            transaction_amount=100,
        )
        assert alert.to_kafka_key() == "cust-abc"

    def test_to_json_dict(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-006",
            customer_id="cust-001",
            fraud_score=0.75,
            rules_triggered=[FraudRuleId.HIGH_VALUE],
            transaction_amount=999.99,
        )
        data = alert.to_json_dict()
        assert data["fraud_score"] == "0.75"
        assert data["transaction_amount"] == "999.99"
        assert isinstance(data["fraud_score"], str)

    def test_detected_at_default(self) -> None:
        alert = FraudAlert(
            transaction_id="txn-007",
            customer_id="cust-001",
            fraud_score=0.8,
            rules_triggered=[FraudRuleId.VELOCITY],
            transaction_amount=100,
        )
        assert isinstance(alert.detected_at, datetime)
