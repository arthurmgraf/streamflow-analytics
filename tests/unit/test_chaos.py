"""Chaos engineering tests for resilience validation.

Tests simulate failure modes that occur in production:
- Corrupted state deserialization
- Extreme input values (boundary conditions)
- Partial state corruption recovery
- ML model unavailability graceful degradation
- DLQ handling under pathological inputs
- Metrics collector thread safety simulation
"""

from __future__ import annotations

import json
import math
import time

import pytest

from src.flink_jobs.common.dlq import build_dlq_record
from src.flink_jobs.common.state import (
    CustomerFraudState,
    GeoLocation,
    RunningStats,
    VelocityWindow,
    haversine_km,
)
from src.flink_jobs.fraud_detector import FraudRuleEvaluator
from src.flink_jobs.ml.feature_engineering import extract_features
from src.utils.metrics import MetricsCollector


class TestStateCorruption:
    """Simulate corrupted state recovery scenarios."""

    def test_running_stats_nan_recovery(self) -> None:
        stats = RunningStats(count=10, mean=float("nan"), m2=100.0)
        data = stats.to_bytes()
        recovered = RunningStats.from_bytes(data)
        assert math.isnan(recovered.mean)
        assert recovered.count == 10

    def test_running_stats_inf_values(self) -> None:
        stats = RunningStats(count=5, mean=float("inf"), m2=float("-inf"))
        data = stats.to_bytes()
        recovered = RunningStats.from_bytes(data)
        assert math.isinf(recovered.mean)
        assert math.isinf(recovered.m2)

    def test_corrupted_bytes_raises(self) -> None:
        with pytest.raises((json.JSONDecodeError, KeyError, TypeError)):
            RunningStats.from_bytes(b"corrupted-garbage-data")

    def test_empty_bytes_raises(self) -> None:
        with pytest.raises((json.JSONDecodeError, KeyError, TypeError)):
            RunningStats.from_bytes(b"")

    def test_partial_json_raises(self) -> None:
        partial = b'{"count": 5, "mean":'
        with pytest.raises((json.JSONDecodeError, KeyError, TypeError)):
            RunningStats.from_bytes(partial)

    def test_wrong_type_json_still_loads(self) -> None:
        wrong = b'{"count": "not_a_number", "mean": 1.0, "m2": 2.0}'
        recovered = RunningStats.from_bytes(wrong)
        assert recovered.mean == 1.0

    def test_geo_location_extreme_coordinates(self) -> None:
        loc = GeoLocation(latitude=90.0, longitude=180.0, timestamp_epoch=0.0)
        data = loc.to_bytes()
        recovered = GeoLocation.from_bytes(data)
        assert recovered.latitude == 90.0
        assert recovered.longitude == 180.0

    def test_geo_location_negative_timestamp(self) -> None:
        loc = GeoLocation(latitude=0.0, longitude=0.0, timestamp_epoch=-1000.0)
        data = loc.to_bytes()
        recovered = GeoLocation.from_bytes(data)
        assert recovered.timestamp_epoch == -1000.0

    def test_velocity_window_massive_list(self) -> None:
        window = VelocityWindow()
        for i in range(10000):
            window.timestamps.append(float(i))
        data = window.to_bytes()
        recovered = VelocityWindow.from_bytes(data)
        assert len(recovered.timestamps) == 10000

    def test_customer_state_all_extremes(self) -> None:
        state = CustomerFraudState(
            amount_stats=RunningStats(count=999999, mean=1e15, m2=1e30),
            hour_stats=RunningStats(count=0, mean=0.0, m2=0.0),
            last_location=GeoLocation(
                latitude=-90.0,
                longitude=-180.0,
                timestamp_epoch=1e12,
            ),
            velocity_window=VelocityWindow(),
            blacklisted=True,
        )
        assert state.amount_stats.count == 999999
        assert state.blacklisted is True
        data = state.amount_stats.to_bytes()
        recovered_stats = RunningStats.from_bytes(data)
        assert recovered_stats.count == 999999
        assert recovered_stats.mean == 1e15


class TestHaversineEdgeCases:
    """Test haversine distance with edge cases."""

    def test_same_point_returns_zero(self) -> None:
        assert haversine_km(0.0, 0.0, 0.0, 0.0) == 0.0

    def test_antipodal_points(self) -> None:
        dist = haversine_km(0.0, 0.0, 0.0, 180.0)
        assert 20000.0 < dist < 20100.0

    def test_poles(self) -> None:
        dist = haversine_km(90.0, 0.0, -90.0, 0.0)
        assert 20000.0 < dist < 20100.0

    def test_nan_coordinates(self) -> None:
        dist = haversine_km(float("nan"), 0.0, 0.0, 0.0)
        assert math.isnan(dist)


class TestExtremeInputs:
    """Test fraud rules with boundary/extreme inputs."""

    @pytest.fixture()
    def evaluator(self) -> FraudRuleEvaluator:
        return FraudRuleEvaluator()

    def test_zero_amount_transaction(self, evaluator: FraudRuleEvaluator) -> None:
        state = CustomerFraudState()
        for _ in range(10):
            state.amount_stats.update(50.0)
        result = evaluator._eval_high_value(state.amount_stats, 0.0)
        assert not result.triggered

    def test_negative_amount_transaction(self, evaluator: FraudRuleEvaluator) -> None:
        state = CustomerFraudState()
        for _ in range(10):
            state.amount_stats.update(50.0)
        result = evaluator._eval_high_value(state.amount_stats, -100.0)
        assert not result.triggered

    def test_massive_amount_transaction(self, evaluator: FraudRuleEvaluator) -> None:
        state = CustomerFraudState()
        for _ in range(10):
            state.amount_stats.update(50.0)
        result = evaluator._eval_high_value(state.amount_stats, 1e12)
        assert result.triggered

    def test_velocity_exactly_at_limit(self, evaluator: FraudRuleEvaluator) -> None:
        now = time.time()
        window = VelocityWindow()
        # _eval_velocity adds current timestamp, so 4 existing + 1 new = 5 = limit
        for i in range(4):
            window.timestamps.append(now - i * 10)
        result = evaluator._eval_velocity(window, now)
        assert not result.triggered

    def test_velocity_one_over_limit(self, evaluator: FraudRuleEvaluator) -> None:
        now = time.time()
        window = VelocityWindow()
        for i in range(6):
            window.timestamps.append(now - i * 10)
        result = evaluator._eval_velocity(window, now)
        assert result.triggered

    def test_geographic_same_location(self, evaluator: FraudRuleEvaluator) -> None:
        last_loc = GeoLocation(
            latitude=-23.5505,
            longitude=-46.6333,
            timestamp_epoch=time.time() - 60,
        )
        result = evaluator._eval_geographic(last_loc, -23.5505, -46.6333, time.time())
        assert not result.triggered

    def test_geographic_antipodal_points(self, evaluator: FraudRuleEvaluator) -> None:
        now = time.time()
        last_loc = GeoLocation(latitude=0.0, longitude=0.0, timestamp_epoch=now - 30)
        result = evaluator._eval_geographic(last_loc, 0.0, 180.0, now)
        assert result.triggered

    def test_time_anomaly_midnight_boundary(self, evaluator: FraudRuleEvaluator) -> None:
        hour_stats = RunningStats()
        for _ in range(25):
            hour_stats.update(12.0)
        midnight_epoch = 1700000000.0
        result = evaluator._eval_time_anomaly(hour_stats, midnight_epoch)
        assert result.rule_id == "FR-004"

    def test_blacklist_false(self, evaluator: FraudRuleEvaluator) -> None:
        result = evaluator._eval_blacklist(False, None)
        assert not result.triggered

    def test_blacklist_true(self, evaluator: FraudRuleEvaluator) -> None:
        result = evaluator._eval_blacklist(True, "store-123")
        assert result.triggered


class TestMLDegradation:
    """Test ML pipeline graceful degradation."""

    def test_feature_extraction_zero_state(self) -> None:
        state = CustomerFraudState()
        features = extract_features(state=state, amount=100.0, hour=12.0)
        assert len(features) == 6
        assert all(isinstance(f, float) for f in features)

    def test_feature_extraction_nan_stats(self) -> None:
        state = CustomerFraudState(
            amount_stats=RunningStats(count=10, mean=float("nan"), m2=100.0),
        )
        features = extract_features(state=state, amount=100.0, hour=12.0)
        assert len(features) == 6
        for f in features:
            assert isinstance(f, float)

    def test_feature_extraction_zero_std_dev(self) -> None:
        state = CustomerFraudState()
        for _ in range(10):
            state.amount_stats.update(100.0)
        features = extract_features(state=state, amount=100.0, hour=12.0)
        assert len(features) == 6
        assert features[0] == 0.0


class TestDLQPathological:
    """Test DLQ handling with pathological inputs."""

    def test_dlq_with_empty_event(self) -> None:
        result = build_dlq_record(
            raw_event="",
            error_type="EmptyEvent",
            error_message="Event was empty",
            source_topic="transactions.raw",
        )
        parsed = json.loads(result)
        assert parsed["error_type"] == "EmptyEvent"
        assert parsed["source_topic"] == "transactions.raw"

    def test_dlq_with_huge_event(self) -> None:
        huge = "x" * 100_000
        result = build_dlq_record(
            raw_event=huge,
            error_type="OversizedEvent",
            error_message="Too large",
            source_topic="transactions.raw",
        )
        parsed = json.loads(result)
        assert len(parsed["raw_event"]) <= 10_000
        assert parsed["truncated"] is True

    def test_dlq_with_unicode_event(self) -> None:
        unicode_str = "Transacao fraudulenta em Sao Paulo"
        result = build_dlq_record(
            raw_event=unicode_str,
            error_type="ValidationError",
            error_message="Campo invalido",
            source_topic="transactions.raw",
        )
        parsed = json.loads(result)
        assert parsed["error_type"] == "ValidationError"

    def test_dlq_with_nested_json(self) -> None:
        nested: dict[str, object] = {"level1": {"level2": {"level3": "deep"}}}
        result = build_dlq_record(
            raw_event=json.dumps(nested),
            error_type="SchemaError",
            error_message="Unexpected nesting",
            source_topic="transactions.raw",
        )
        parsed = json.loads(result)
        assert "raw_event" in parsed

    def test_dlq_preserves_processor_name(self) -> None:
        result = build_dlq_record(
            raw_event="bad-data",
            error_type="ParseError",
            error_message="Invalid JSON",
            source_topic="transactions.raw",
            processor="transaction-processor",
        )
        parsed = json.loads(result)
        assert parsed["processor"] == "transaction-processor"


class TestMetricsResilience:
    """Test MetricsCollector under stress."""

    def test_counter_overflow_simulation(self) -> None:
        collector = MetricsCollector()
        for _ in range(100_000):
            collector.inc_counter("stress_test", 1.0)
        assert collector.get_counter("stress_test") == 100_000.0

    def test_histogram_memory_growth(self) -> None:
        collector = MetricsCollector()
        for i in range(10_000):
            collector.observe_histogram("latency", float(i) / 1000)
        values = collector.get_histogram("latency")
        assert len(values) == 10_000

    def test_gauge_rapid_updates(self) -> None:
        collector = MetricsCollector()
        for i in range(10_000):
            collector.set_gauge("active_jobs", float(i))
        assert collector.get_gauge("active_jobs") == 9999.0

    def test_timer_zero_duration(self) -> None:
        collector = MetricsCollector()
        with collector.timer("fast_op"):
            pass
        values = collector.get_histogram("fast_op")
        assert len(values) == 1
        assert values[0] >= 0.0

    def test_snapshot_under_load(self) -> None:
        collector = MetricsCollector()
        for i in range(1000):
            collector.inc_counter(f"counter_{i % 10}", 1.0)
            collector.set_gauge(f"gauge_{i % 5}", float(i))
        snap = collector.snapshot()
        assert len(snap["counters"]) == 10
        assert len(snap["gauges"]) == 5

    def test_reset_clears_everything(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter("test", 100.0)
        collector.set_gauge("test", 50.0)
        collector.observe_histogram("test", 1.0)
        collector.reset()
        assert collector.get_counter("test") == 0.0
        assert collector.get_gauge("test") == 0.0
        assert collector.get_histogram("test") == []
