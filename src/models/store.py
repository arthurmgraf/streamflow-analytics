"""Store model."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Store(BaseModel):
    """Physical or online store."""

    store_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., max_length=2, min_length=2)
    latitude: float | None = Field(None, ge=-90, le=90)
    longitude: float | None = Field(None, ge=-180, le=180)
    category: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
