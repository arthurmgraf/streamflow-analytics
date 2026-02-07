"""Customer model."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, Field


class RiskProfile(StrEnum):
    """Customer risk classification."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Customer(BaseModel):
    """Customer profile for enrichment and fraud detection."""

    customer_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    email: str | None = None
    city: str | None = None
    state: str | None = Field(None, max_length=2)
    avg_transaction_amt: Decimal = Field(default=Decimal("0"), ge=0)
    total_transactions: int = Field(default=0, ge=0)
    risk_profile: RiskProfile = Field(default=RiskProfile.NORMAL)
    first_seen_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
