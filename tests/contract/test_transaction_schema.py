"""Contract tests for Transaction schema.

These tests define the schema contract between producers (generators) and
consumers (Flink jobs, Airflow DAGs). Any schema change that breaks these
tests requires a coordinated update across all components.

Contract guarantees:
    - Required fields are always present in serialized output
    - Field types match expected types
    - Pydantic validation rejects invalid data
    - Serialization format is stable across versions
"""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal

import pytest

from src.flink_jobs.common.serialization import (
    CURRENT_SCHEMA_VERSION,
    deserialize_transaction,
    serialize_transaction,
)
from src.models.transaction import Transaction

pytestmark = pytest.mark.contract

REQUIRED_FIELDS = {"transaction_id", "customer_id", "store_id", "amount", "currency", "timestamp"}
OPTIONAL_FIELDS = {"product_id", "payment_method", "latitude", "longitude"}


class TestTransactionSchemaContract:
    """Contract: Transaction model field requirements."""

    def test_required_fields_present(self) -> None:
        txn = Transaction(
            transaction_id="txn-001",
            customer_id="cust-001",
            store_id="store-001",
            amount=Decimal("100.00"),
            timestamp=datetime(2026, 1, 15, 10, 30),
        )
        json_dict = txn.to_json_dict()
        for field in REQUIRED_FIELDS:
            assert field in json_dict, f"Required field '{field}' missing from serialized output"

    def test_optional_fields_allowed_none(self) -> None:
        txn = Transaction(
            transaction_id="txn-002",
            customer_id="cust-002",
            store_id="store-002",
            amount=Decimal("50.00"),
            timestamp=datetime(2026, 1, 15),
        )
        assert txn.product_id is None
        assert txn.payment_method is None
        assert txn.latitude is None
        assert txn.longitude is None

    def test_amount_must_be_positive(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="txn-neg",
                customer_id="cust-neg",
                store_id="store-neg",
                amount=Decimal("-10.00"),
                timestamp=datetime(2026, 1, 15),
            )

    def test_amount_zero_rejected(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="txn-zero",
                customer_id="cust-zero",
                store_id="store-zero",
                amount=Decimal("0.00"),
                timestamp=datetime(2026, 1, 15),
            )

    def test_currency_format(self) -> None:
        txn = Transaction(
            transaction_id="txn-cur",
            customer_id="cust-cur",
            store_id="store-cur",
            amount=Decimal("100.00"),
            timestamp=datetime(2026, 1, 15),
        )
        assert txn.currency == "BRL"
        assert len(txn.currency) == 3
        assert txn.currency.isupper()

    def test_invalid_currency_rejected(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="txn-bad-cur",
                customer_id="cust-bad-cur",
                store_id="store-bad-cur",
                amount=Decimal("100.00"),
                currency="invalid",
                timestamp=datetime(2026, 1, 15),
            )

    def test_latitude_range(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="txn-lat",
                customer_id="cust-lat",
                store_id="store-lat",
                amount=Decimal("100.00"),
                latitude=91.0,
                timestamp=datetime(2026, 1, 15),
            )

    def test_longitude_range(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="txn-lon",
                customer_id="cust-lon",
                store_id="store-lon",
                amount=Decimal("100.00"),
                longitude=181.0,
                timestamp=datetime(2026, 1, 15),
            )

    def test_empty_transaction_id_rejected(self) -> None:
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="",
                customer_id="cust-empty",
                store_id="store-empty",
                amount=Decimal("100.00"),
                timestamp=datetime(2026, 1, 15),
            )

    def test_amount_coercion_from_string(self) -> None:
        txn = Transaction(
            transaction_id="txn-str",
            customer_id="cust-str",
            store_id="store-str",
            amount="199.99",  # type: ignore[arg-type]
            timestamp=datetime(2026, 1, 15),
        )
        assert txn.amount == Decimal("199.99")

    def test_amount_coercion_from_float(self) -> None:
        txn = Transaction(
            transaction_id="txn-float",
            customer_id="cust-float",
            store_id="store-float",
            amount=199.99,  # type: ignore[arg-type]
            timestamp=datetime(2026, 1, 15),
        )
        assert isinstance(txn.amount, Decimal)


class TestTransactionSerializationContract:
    """Contract: Serialized Transaction format for Kafka."""

    def _make_transaction(self) -> Transaction:
        return Transaction(
            transaction_id="txn-ser-001",
            customer_id="cust-ser-001",
            store_id="store-ser-001",
            amount=Decimal("250.50"),
            currency="BRL",
            latitude=-23.55,
            longitude=-46.63,
            timestamp=datetime(2026, 1, 15, 14, 30),
        )

    def test_serialized_is_valid_json(self) -> None:
        txn = self._make_transaction()
        serialized = serialize_transaction(txn)
        parsed = json.loads(serialized)
        assert isinstance(parsed, dict)

    def test_amount_serialized_as_string(self) -> None:
        txn = self._make_transaction()
        serialized = serialize_transaction(txn)
        parsed = json.loads(serialized)
        assert isinstance(parsed["amount"], str)
        assert Decimal(parsed["amount"]) == Decimal("250.50")

    def test_roundtrip_preserves_data(self) -> None:
        txn = self._make_transaction()
        roundtripped = deserialize_transaction(serialize_transaction(txn))
        assert roundtripped is not None
        assert roundtripped.transaction_id == txn.transaction_id
        assert roundtripped.customer_id == txn.customer_id
        assert roundtripped.store_id == txn.store_id
        assert roundtripped.amount == txn.amount

    def test_malformed_json_returns_none(self) -> None:
        assert deserialize_transaction("not-json") is None

    def test_missing_required_field_returns_none(self) -> None:
        incomplete = json.dumps({"transaction_id": "txn-001", "amount": "100"})
        assert deserialize_transaction(incomplete) is None

    def test_kafka_key_is_customer_id(self) -> None:
        txn = self._make_transaction()
        assert txn.to_kafka_key() == "cust-ser-001"

    def test_schema_version_forward_compat(self) -> None:
        future = json.dumps(
            {
                "schema_version": CURRENT_SCHEMA_VERSION + 1,
                "transaction_id": "txn-future",
                "customer_id": "cust-future",
                "store_id": "store-future",
                "amount": "100.00",
                "currency": "BRL",
                "timestamp": "2026-01-15T10:00:00",
                "new_field_from_future": "ignored",
            }
        )
        result = deserialize_transaction(future)
        assert result is not None
        assert result.transaction_id == "txn-future"

    def test_current_schema_version_is_integer(self) -> None:
        assert isinstance(CURRENT_SCHEMA_VERSION, int)
        assert CURRENT_SCHEMA_VERSION >= 1
