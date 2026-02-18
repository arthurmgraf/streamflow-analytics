"""State management helpers for PyFlink fraud detection.

Provides serializable state objects used by both:
- FraudRuleEvaluator (pure Python, stateless evaluation)
- FraudDetectorFunction (Flink KeyedProcessFunction with ValueState/ListState)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field


@dataclass
class RunningStats:
    """Incremental running statistics (mean, std dev) without storing all values.

    Uses Welford's online algorithm for numerically stable, O(1) memory computation.
    """

    count: int = 0
    mean: float = 0.0
    m2: float = 0.0

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

    def to_bytes(self) -> bytes:
        """Serialize to bytes for Flink ValueState persistence."""
        return json.dumps({"count": self.count, "mean": self.mean, "m2": self.m2}).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> RunningStats:
        """Deserialize from bytes stored in Flink ValueState."""
        obj = json.loads(data.decode("utf-8"))
        return cls(count=obj["count"], mean=obj["mean"], m2=obj["m2"])


@dataclass
class GeoLocation:
    """Geographic coordinates with timestamp."""

    latitude: float
    longitude: float
    timestamp_epoch: float

    def to_bytes(self) -> bytes:
        """Serialize to bytes for Flink ValueState persistence."""
        return json.dumps(
            {
                "latitude": self.latitude,
                "longitude": self.longitude,
                "timestamp_epoch": self.timestamp_epoch,
            }
        ).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> GeoLocation:
        """Deserialize from bytes stored in Flink ValueState."""
        obj = json.loads(data.decode("utf-8"))
        return cls(
            latitude=obj["latitude"],
            longitude=obj["longitude"],
            timestamp_epoch=obj["timestamp_epoch"],
        )


@dataclass
class VelocityWindow:
    """Sliding window of transaction timestamps for velocity detection."""

    timestamps: list[float] = field(default_factory=list)

    def add(self, timestamp: float) -> None:
        self.timestamps.append(timestamp)

    def prune(self, cutoff: float) -> None:
        """Remove timestamps older than cutoff."""
        self.timestamps = [t for t in self.timestamps if t > cutoff]

    @property
    def count(self) -> int:
        return len(self.timestamps)

    def to_bytes(self) -> bytes:
        """Serialize to bytes for Flink ListState persistence."""
        return json.dumps(self.timestamps).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> VelocityWindow:
        """Deserialize from bytes stored in Flink ListState."""
        timestamps = json.loads(data.decode("utf-8"))
        return cls(timestamps=timestamps)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points on Earth in kilometers."""
    r = 6371.0
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


@dataclass
class CustomerFraudState:
    """Aggregated per-customer state for fraud detection.

    Encapsulates all state needed by FraudRuleEvaluator.
    In Flink, each field is backed by ValueState<bytes>.
    """

    amount_stats: RunningStats = field(default_factory=RunningStats)
    hour_stats: RunningStats = field(default_factory=RunningStats)
    velocity_window: VelocityWindow = field(default_factory=VelocityWindow)
    last_location: GeoLocation | None = None
    blacklisted: bool = False
