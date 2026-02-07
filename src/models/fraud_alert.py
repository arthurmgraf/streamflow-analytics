"""Fraud alert model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class FraudRuleId(StrEnum):
    """Fraud detection rule identifiers."""

    HIGH_VALUE = "FR-001"
    VELOCITY = "FR-002"
    GEOGRAPHIC = "FR-003"
    TIME_ANOMALY = "FR-004"
    BLACKLIST = "FR-005"
    ML_ANOMALY = "FR-006"


class FraudAlert(BaseModel):
    """Alert generated when a transaction triggers fraud rules."""

    transaction_id: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    alert_type: str = Field(default="fraud_suspected")
    fraud_score: Decimal = Field(..., ge=0, le=1, max_digits=4, decimal_places=3)
    rules_triggered: list[FraudRuleId] = Field(..., min_length=1)
    rule_details: dict[str, object] = Field(default_factory=dict)
    transaction_amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    detected_at: datetime = Field(default_factory=datetime.now)

    @field_validator("fraud_score", mode="before")
    @classmethod
    def coerce_fraud_score(cls, v: object) -> Decimal:
        """Coerce numeric types to Decimal."""
        return Decimal(str(v))

    @field_validator("transaction_amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: object) -> Decimal:
        """Coerce numeric types to Decimal."""
        return Decimal(str(v))

    def to_kafka_key(self) -> str:
        """Partition key for Kafka (group alerts by customer)."""
        return self.customer_id

    def to_json_dict(self) -> dict[str, object]:
        """Serialize to JSON-compatible dict for Kafka."""
        data = self.model_dump(mode="json")
        data["fraud_score"] = str(self.fraud_score)
        data["transaction_amount"] = str(self.transaction_amount)
        return data
