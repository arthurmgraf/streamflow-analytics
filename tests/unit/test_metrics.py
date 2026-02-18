"""Unit tests for metrics collector."""

from __future__ import annotations

import time

from src.utils.metrics import (
    DLQ_EVENTS_TOTAL,
    FRAUD_ALERTS_TOTAL,
    PROCESSING_LATENCY_SECONDS,
    TRANSACTIONS_PROCESSED_TOTAL,
    MetricsCollector,
)


class TestMetricsCollector:
    def test_increment_counter(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter(TRANSACTIONS_PROCESSED_TOTAL, status="success")
        assert collector.get_counter(TRANSACTIONS_PROCESSED_TOTAL, status="success") == 1.0

    def test_increment_counter_multiple(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter(FRAUD_ALERTS_TOTAL, value=3.0, rule_id="FR-001")
        collector.inc_counter(FRAUD_ALERTS_TOTAL, value=2.0, rule_id="FR-001")
        assert collector.get_counter(FRAUD_ALERTS_TOTAL, rule_id="FR-001") == 5.0

    def test_counter_different_labels(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter(DLQ_EVENTS_TOTAL, topic="transactions")
        collector.inc_counter(DLQ_EVENTS_TOTAL, topic="alerts")
        assert collector.get_counter(DLQ_EVENTS_TOTAL, topic="transactions") == 1.0
        assert collector.get_counter(DLQ_EVENTS_TOTAL, topic="alerts") == 1.0

    def test_set_gauge(self) -> None:
        collector = MetricsCollector()
        collector.set_gauge("consumer_lag", 500.0, group="fraud-detector")
        assert collector.get_gauge("consumer_lag", group="fraud-detector") == 500.0

    def test_gauge_overwrite(self) -> None:
        collector = MetricsCollector()
        collector.set_gauge("consumer_lag", 100.0)
        collector.set_gauge("consumer_lag", 200.0)
        assert collector.get_gauge("consumer_lag") == 200.0

    def test_observe_histogram(self) -> None:
        collector = MetricsCollector()
        collector.observe_histogram(PROCESSING_LATENCY_SECONDS, 0.5)
        collector.observe_histogram(PROCESSING_LATENCY_SECONDS, 1.2)
        collector.observe_histogram(PROCESSING_LATENCY_SECONDS, 0.3)
        values = collector.get_histogram(PROCESSING_LATENCY_SECONDS)
        assert len(values) == 3
        assert values[0] == 0.5

    def test_timer_context_manager(self) -> None:
        collector = MetricsCollector()
        with collector.timer("test_duration"):
            time.sleep(0.05)
        values = collector.get_histogram("test_duration")
        assert len(values) == 1
        assert values[0] >= 0.01

    def test_snapshot(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter("c1")
        collector.set_gauge("g1", 10.0)
        collector.observe_histogram("h1", 0.5)
        snap = collector.snapshot()
        assert "counters" in snap
        assert "gauges" in snap
        assert "histograms" in snap

    def test_reset(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter("test_counter")
        collector.reset()
        assert collector.get_counter("test_counter") == 0.0

    def test_empty_labels(self) -> None:
        collector = MetricsCollector()
        collector.inc_counter("no_labels")
        assert collector.get_counter("no_labels") == 1.0

    def test_nonexistent_counter_returns_zero(self) -> None:
        collector = MetricsCollector()
        assert collector.get_counter("nonexistent") == 0.0
