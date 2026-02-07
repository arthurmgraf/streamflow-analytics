"""Transaction event model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class Transaction(BaseModel):
    """E-commerce transaction event."""

    transaction_id: str = Field(..., min_length=1, description="Unique transaction identifier")
    customer_id: str = Field(..., min_length=1, description="Customer who made the transaction")
    store_id: str = Field(..., min_length=1, description="Store where the transaction occurred")
    product_id: str | None = Field(None, description="Product purchased")
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")
    payment_method: str | None = Field(None, description="Payment method used")
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    timestamp: datetime = Field(..., description="When the transaction occurred")

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: object) -> Decimal:
        """Coerce numeric types to Decimal."""
        return Decimal(str(v))

    def to_kafka_key(self) -> str:
        """Partition key for Kafka (ensures ordering per customer)."""
        return self.customer_id

    def to_json_dict(self) -> dict[str, object]:
        """Serialize to JSON-compatible dict for Kafka."""
        data = self.model_dump(mode="json")
        data["amount"] = str(self.amount)
        return data
