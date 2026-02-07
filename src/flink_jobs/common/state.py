"""State management helpers for PyFlink fraud detection."""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass
class RunningStats:
    """Incremental running statistics (mean, std dev) without storing all values."""

    count: int = 0
    mean: float = 0.0
    m2: float = 0.0  # Sum of squares of differences from the mean

    def update(self, value: float) -> None:
        """Update statistics with a new value (Welford's algorithm)."""
        self.count += 1
        delta = value - self.mean
        self.mean += delta / self.count
        delta2 = value - self.mean
        self.m2 += delta * delta2

    @property
    def variance(self) -> float:
        if self.count < 2:
            return 0.0
        return self.m2 / (self.count - 1)

    @property
    def std_dev(self) -> float:
        return math.sqrt(self.variance)


@dataclass
class GeoLocation:
    """Geographic coordinates with timestamp."""

    latitude: float
    longitude: float
    timestamp_epoch: float


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points on Earth in kilometers."""
    r = 6371.0  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return r * c


@dataclass
class FraudRuleResult:
    """Result from a single fraud rule evaluation."""

    rule_id: str
    score: float  # 0.0 to 1.0
    triggered: bool = False
    details: dict[str, object] = field(default_factory=dict)
