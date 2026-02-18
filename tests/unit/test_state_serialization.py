"""Unit tests for state serialization (to_bytes / from_bytes)."""

from __future__ import annotations

from src.flink_jobs.common.state import (
    CustomerFraudState,
    GeoLocation,
    RunningStats,
    VelocityWindow,
)


class TestRunningStatsSerialization:
    """Tests for RunningStats byte serialization."""

    def test_empty_roundtrip(self) -> None:
        stats = RunningStats()
        restored = RunningStats.from_bytes(stats.to_bytes())
        assert restored.count == 0
        assert restored.mean == 0.0
        assert restored.m2 == 0.0

    def test_populated_roundtrip(self) -> None:
        stats = RunningStats()
        for v in [10.0, 20.0, 30.0, 40.0, 50.0]:
            stats.update(v)
        restored = RunningStats.from_bytes(stats.to_bytes())
        assert restored.count == 5
        assert abs(restored.mean - 30.0) < 1e-9
        assert abs(restored.m2 - stats.m2) < 1e-9
        assert abs(restored.std_dev - stats.std_dev) < 1e-9

    def test_single_value_roundtrip(self) -> None:
        stats = RunningStats()
        stats.update(42.0)
        restored = RunningStats.from_bytes(stats.to_bytes())
        assert restored.count == 1
        assert restored.mean == 42.0
        assert restored.std_dev == 0.0


class TestGeoLocationSerialization:
    """Tests for GeoLocation byte serialization."""

    def test_roundtrip(self) -> None:
        loc = GeoLocation(latitude=-23.5505, longitude=-46.6333, timestamp_epoch=1700000000.0)
        restored = GeoLocation.from_bytes(loc.to_bytes())
        assert restored.latitude == -23.5505
        assert restored.longitude == -46.6333
        assert restored.timestamp_epoch == 1700000000.0

    def test_extreme_coordinates(self) -> None:
        loc = GeoLocation(latitude=90.0, longitude=-180.0, timestamp_epoch=0.0)
        restored = GeoLocation.from_bytes(loc.to_bytes())
        assert restored.latitude == 90.0
        assert restored.longitude == -180.0


class TestVelocityWindowSerialization:
    """Tests for VelocityWindow byte serialization."""

    def test_empty_roundtrip(self) -> None:
        window = VelocityWindow()
        restored = VelocityWindow.from_bytes(window.to_bytes())
        assert restored.count == 0

    def test_populated_roundtrip(self) -> None:
        window = VelocityWindow()
        timestamps = [1000.0, 1010.0, 1020.0, 1030.0]
        for ts in timestamps:
            window.add(ts)
        restored = VelocityWindow.from_bytes(window.to_bytes())
        assert restored.count == 4
        assert restored.timestamps == timestamps

    def test_prune_then_serialize(self) -> None:
        window = VelocityWindow()
        for ts in [100.0, 200.0, 300.0, 400.0]:
            window.add(ts)
        window.prune(250.0)
        restored = VelocityWindow.from_bytes(window.to_bytes())
        assert restored.count == 2
        assert 100.0 not in restored.timestamps
        assert 300.0 in restored.timestamps


class TestCustomerFraudStateComposition:
    """Tests for CustomerFraudState as composition of sub-states."""

    def test_default_state(self) -> None:
        state = CustomerFraudState()
        assert state.amount_stats.count == 0
        assert state.hour_stats.count == 0
        assert state.velocity_window.count == 0
        assert state.last_location is None
        assert state.blacklisted is False

    def test_state_with_location(self) -> None:
        state = CustomerFraudState(
            last_location=GeoLocation(
                latitude=-23.55, longitude=-46.63, timestamp_epoch=1700000000.0
            )
        )
        assert state.last_location is not None
        assert state.last_location.latitude == -23.55

    def test_independent_sub_states(self) -> None:
        state = CustomerFraudState()
        state.amount_stats.update(100.0)
        state.hour_stats.update(14.0)
        state.velocity_window.add(1000.0)
        assert state.amount_stats.count == 1
        assert state.hour_stats.count == 1
        assert state.velocity_window.count == 1
        assert state.amount_stats.mean == 100.0
        assert state.hour_stats.mean == 14.0

    def test_full_state_roundtrip(self) -> None:
        state = CustomerFraudState()
        state.amount_stats.update(100.0)
        state.amount_stats.update(200.0)
        state.hour_stats.update(10.0)
        state.velocity_window.add(1000.0)
        state.velocity_window.add(1010.0)
        state.last_location = GeoLocation(latitude=-23.55, longitude=-46.63, timestamp_epoch=1000.0)
        state.blacklisted = True

        amount_restored = RunningStats.from_bytes(state.amount_stats.to_bytes())
        hour_restored = RunningStats.from_bytes(state.hour_stats.to_bytes())
        vel_restored = VelocityWindow.from_bytes(state.velocity_window.to_bytes())
        loc_restored = GeoLocation.from_bytes(state.last_location.to_bytes())

        assert amount_restored.count == 2
        assert abs(amount_restored.mean - 150.0) < 1e-9
        assert hour_restored.count == 1
        assert vel_restored.count == 2
        assert loc_restored.latitude == -23.55
