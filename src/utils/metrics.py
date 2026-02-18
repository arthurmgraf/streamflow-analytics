"""Application metrics for Prometheus instrumentation.

Provides a lightweight metrics registry for custom business metrics.
In production (Flink), these are exposed via Flink's Prometheus reporter.
This module defines the metric names and labels as constants for consistency
across all components.

Metric naming convention: streamflow_{component}_{metric}_{unit}
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

TRANSACTIONS_PROCESSED_TOTAL = "streamflow_transactions_processed_total"
FRAUD_ALERTS_TOTAL = "streamflow_fraud_alerts_total"
DLQ_EVENTS_TOTAL = "streamflow_dlq_events_total"
PROCESSING_LATENCY_SECONDS = "streamflow_processing_latency_seconds"
RULE_EVALUATIONS_TOTAL = "streamflow_rule_evaluations_total"
ML_SCORES_HISTOGRAM = "streamflow_ml_anomaly_score"
CHECKPOINT_DURATION_SECONDS = "streamflow_checkpoint_duration_seconds"
SCHEMA_VERSION_INFO = "streamflow_schema_version_info"

LABEL_JOB = "job_name"
LABEL_RULE = "rule_id"
LABEL_STATUS = "status"
LABEL_TOPIC = "topic"


class MetricsCollector:
    """In-process metrics collector.

    Collects counters and histograms in memory. In production, Flink's
    Prometheus reporter handles exposition. This collector is used for:
    - Structured log enrichment
    - Testing metric emission
    - Airflow DAG metric reporting
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: dict[str, list[float]] = defaultdict(list)

    def inc_counter(self, name: str, value: float = 1.0, **labels: str) -> None:
        label_key = _labels_to_key(labels)
        with self._lock:
            self._counters[name][label_key] += value

    def set_gauge(self, name: str, value: float, **labels: str) -> None:
        label_key = _labels_to_key(labels)
        with self._lock:
            self._gauges[name][label_key] = value

    def observe_histogram(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms[name].append(value)

    @contextmanager
    def timer(self, metric_name: str) -> Generator[None, None, None]:
        """Context manager to time a block and record as histogram."""
        start = time.monotonic()
        try:
            yield
        finally:
            elapsed = time.monotonic() - start
            self.observe_histogram(metric_name, elapsed)

    def get_counter(self, name: str, **labels: str) -> float:
        label_key = _labels_to_key(labels)
        with self._lock:
            return self._counters[name][label_key]

    def get_gauge(self, name: str, **labels: str) -> float:
        label_key = _labels_to_key(labels)
        with self._lock:
            return self._gauges[name][label_key]

    def get_histogram(self, name: str) -> list[float]:
        with self._lock:
            return list(self._histograms[name])

    def snapshot(self) -> dict[str, Any]:
        """Return a snapshot of all collected metrics."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {k: len(v) for k, v in self._histograms.items()},
            }

    def reset(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


def _labels_to_key(labels: dict[str, str]) -> str:
    if not labels:
        return ""
    return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))


_default_collector: MetricsCollector | None = None


def get_collector() -> MetricsCollector:
    """Get or create the default metrics collector."""
    global _default_collector
    if _default_collector is None:
        _default_collector = MetricsCollector()
    return _default_collector
