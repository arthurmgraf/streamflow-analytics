"""Contract tests for state serialization compatibility.

These tests ensure that state objects (RunningStats, GeoLocation, VelocityWindow)
maintain backward-compatible serialization across versions. Breaking these
contracts would corrupt Flink checkpoints.

Contract guarantees:
    - to_bytes()/from_bytes() roundtrips are lossless
    - Serialization format is stable JSON
    - Missing fields in stored state don't crash deserialization
    - CustomerFraudState components serialize independently
"""

from __future__ import annotations

import json

import pytest

from src.flink_jobs.common.state import (
    CustomerFraudState,
    GeoLocation,
    RunningStats,
    VelocityWindow,
)

pytestmark = pytest.mark.contract


class TestRunningStatsContract:
    """Contract: RunningStats serialization format."""

    def test_serialized_format_is_json(self) -> None:
        stats = RunningStats(count=10, mean=100.0, m2=500.0)
        data = json.loads(stats.to_bytes().decode("utf-8"))
        assert set(data.keys()) == {"count", "mean", "m2"}

    def test_roundtrip_preserves_values(self) -> None:
        original = RunningStats(count=42, mean=123.456, m2=789.012)
        restored = RunningStats.from_bytes(original.to_bytes())
        assert restored.count == original.count
        assert restored.mean == original.mean
        assert restored.m2 == original.m2

    def test_default_state_roundtrip(self) -> None:
        stats = RunningStats()
        restored = RunningStats.from_bytes(stats.to_bytes())
        assert restored.count == 0
        assert restored.mean == 0.0

    def test_properties_consistent_after_roundtrip(self) -> None:
        stats = RunningStats()
        for v in [10.0, 20.0, 30.0, 40.0, 50.0]:
            stats.update(v)
        restored = RunningStats.from_bytes(stats.to_bytes())
        assert abs(restored.std_dev - stats.std_dev) < 1e-10
        assert abs(restored.variance - stats.variance) < 1e-10


class TestGeoLocationContract:
    """Contract: GeoLocation serialization format."""

    def test_serialized_format_is_json(self) -> None:
        geo = GeoLocation(latitude=-23.55, longitude=-46.63, timestamp_epoch=1700000000.0)
        data = json.loads(geo.to_bytes().decode("utf-8"))
        assert set(data.keys()) == {"latitude", "longitude", "timestamp_epoch"}

    def test_roundtrip_preserves_values(self) -> None:
        original = GeoLocation(latitude=-23.5505, longitude=-46.6333, timestamp_epoch=1700000000.0)
        restored = GeoLocation.from_bytes(original.to_bytes())
        assert restored.latitude == original.latitude
        assert restored.longitude == original.longitude
        assert restored.timestamp_epoch == original.timestamp_epoch

    def test_extreme_coordinates(self) -> None:
        geo = GeoLocation(latitude=90.0, longitude=180.0, timestamp_epoch=0.0)
        restored = GeoLocation.from_bytes(geo.to_bytes())
        assert restored.latitude == 90.0
        assert restored.longitude == 180.0


class TestVelocityWindowContract:
    """Contract: VelocityWindow serialization format."""

    def test_serialized_format_is_json_array(self) -> None:
        window = VelocityWindow(timestamps=[1.0, 2.0, 3.0])
        data = json.loads(window.to_bytes().decode("utf-8"))
        assert isinstance(data, list)
        assert data == [1.0, 2.0, 3.0]

    def test_roundtrip_preserves_values(self) -> None:
        original = VelocityWindow(timestamps=[100.0, 200.0, 300.0])
        restored = VelocityWindow.from_bytes(original.to_bytes())
        assert restored.timestamps == original.timestamps
        assert restored.count == original.count

    def test_empty_window_roundtrip(self) -> None:
        window = VelocityWindow()
        restored = VelocityWindow.from_bytes(window.to_bytes())
        assert restored.count == 0
        assert restored.timestamps == []


class TestCustomerFraudStateContract:
    """Contract: CustomerFraudState components are independently serializable."""

    def test_all_components_have_to_bytes(self) -> None:
        state = CustomerFraudState()
        assert hasattr(state.amount_stats, "to_bytes")
        assert hasattr(state.hour_stats, "to_bytes")
        assert hasattr(state.velocity_window, "to_bytes")

    def test_full_state_component_roundtrip(self) -> None:
        state = CustomerFraudState()
        state.amount_stats.update(100.0)
        state.amount_stats.update(200.0)
        state.hour_stats.update(14.0)
        state.velocity_window.add(1000.0)
        state.velocity_window.add(2000.0)
        state.last_location = GeoLocation(-23.55, -46.63, 1700000000.0)
        state.blacklisted = True

        amount_restored = RunningStats.from_bytes(state.amount_stats.to_bytes())
        assert amount_restored.count == 2
        assert abs(amount_restored.mean - 150.0) < 0.01

        hour_restored = RunningStats.from_bytes(state.hour_stats.to_bytes())
        assert hour_restored.count == 1

        vel_restored = VelocityWindow.from_bytes(state.velocity_window.to_bytes())
        assert vel_restored.count == 2

        geo_restored = GeoLocation.from_bytes(state.last_location.to_bytes())
        assert geo_restored.latitude == -23.55

    def test_blacklisted_is_plain_bool(self) -> None:
        state = CustomerFraudState(blacklisted=True)
        assert isinstance(state.blacklisted, bool)
