"""Fraud detection engine with 5 rule-based detectors.

Reads transactions from Kafka, evaluates fraud rules using keyed state,
and produces FraudAlert events for transactions exceeding the threshold.

Rules:
    FR-001: High Value — Transaction > multiplier * customer average
    FR-002: Velocity — Too many transactions in a time window
    FR-003: Geographic — Impossible travel detection
    FR-004: Time Anomaly — Transaction at unusual hour for customer
    FR-005: Blacklist — Customer/store on known fraud list
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from src.flink_jobs.common.state import (
    FraudRuleResult,
    GeoLocation,
    RunningStats,
    haversine_km,
)
from src.models.fraud_alert import FraudAlert, FraudRuleId

logger = logging.getLogger(__name__)

# Default rule configs (overridden by config/fraud_rules.yaml)
DEFAULT_RULES_CONFIG: dict[str, Any] = {
    "high_value": {"multiplier": 3.0, "min_transactions": 5, "weight": 0.30},
    "velocity": {"max_count": 5, "window_minutes": 10, "weight": 0.25},
    "geographic": {"max_distance_km": 500, "max_time_hours": 1, "weight": 0.20},
    "time_anomaly": {"std_dev_threshold": 2.0, "weight": 0.15},
    "blacklist": {"weight": 0.10},
}

ALERT_THRESHOLD = 0.7


class FraudEngine:
    """Stateful fraud detection engine.

    Maintains per-customer state for evaluating all 5 rules.
    Designed to work with PyFlink KeyedProcessFunction state,
    but also usable standalone for testing.
    """

    def __init__(self, rules_config: dict[str, Any] | None = None) -> None:
        self.config = rules_config or DEFAULT_RULES_CONFIG
        self.threshold = self.config.get("alert_threshold", ALERT_THRESHOLD)

        # Per-customer state (in Flink, these would be ValueState)
        self._amount_stats: dict[str, RunningStats] = {}
        self._velocity_windows: dict[str, list[float]] = {}
        self._last_locations: dict[str, GeoLocation] = {}
        self._hour_stats: dict[str, RunningStats] = {}
        self._blacklist: set[str] = set()

    def set_blacklist(self, blacklisted_ids: set[str]) -> None:
        """Update the blacklist (called via broadcast state in Flink)."""
        self._blacklist = blacklisted_ids

    def evaluate(
        self,
        customer_id: str,
        amount: float,
        timestamp_epoch: float,
        latitude: float | None = None,
        longitude: float | None = None,
        store_id: str | None = None,
    ) -> tuple[float, list[FraudRuleResult]]:
        """Evaluate all fraud rules for a transaction.

        Returns:
            Tuple of (weighted_score, list of rule results).
        """
        results: list[FraudRuleResult] = []

        results.append(self._eval_high_value(customer_id, amount))
        results.append(self._eval_velocity(customer_id, timestamp_epoch))
        results.append(
            self._eval_geographic(customer_id, latitude, longitude, timestamp_epoch)
        )
        results.append(self._eval_time_anomaly(customer_id, timestamp_epoch))
        results.append(self._eval_blacklist(customer_id, store_id))

        # Weighted average of triggered rules
        total_weight = 0.0
        weighted_sum = 0.0
        for result in results:
            rule_key = self._rule_id_to_config_key(result.rule_id)
            weight = self.config.get(rule_key, {}).get("weight", 0.2)
            if result.triggered:
                weighted_sum += result.score * weight
                total_weight += weight

        final_score = weighted_sum / total_weight if total_weight > 0 else 0.0
        return final_score, results

    def process_transaction(
        self,
        transaction_data: dict[str, Any],
    ) -> FraudAlert | None:
        """Process a single transaction and return alert if threshold exceeded."""
        customer_id = transaction_data["customer_id"]
        amount = float(transaction_data["amount"])
        timestamp_epoch = transaction_data.get("timestamp_epoch", time.time())

        score, results = self.evaluate(
            customer_id=customer_id,
            amount=amount,
            timestamp_epoch=timestamp_epoch,
            latitude=transaction_data.get("latitude"),
            longitude=transaction_data.get("longitude"),
            store_id=transaction_data.get("store_id"),
        )

        if score >= self.threshold:
            triggered_rules = [
                FraudRuleId(r.rule_id) for r in results if r.triggered
            ]
            rule_details: dict[str, object] = {
                r.rule_id: asdict(r) for r in results if r.triggered
            }

            return FraudAlert(
                transaction_id=transaction_data["transaction_id"],
                customer_id=customer_id,
                fraud_score=Decimal(str(round(score, 3))),
                rules_triggered=triggered_rules,
                rule_details=rule_details,
                transaction_amount=Decimal(str(amount)),
            )
        return None

    # --- Individual Rules ---

    def _eval_high_value(self, customer_id: str, amount: float) -> FraudRuleResult:
        """FR-001: High Value — transaction > multiplier * customer average."""
        cfg = self.config.get("high_value", {})
        multiplier = cfg.get("multiplier", 3.0)
        min_txns = cfg.get("min_transactions", 5)

        stats = self._amount_stats.setdefault(customer_id, RunningStats())
        count_before = stats.count
        avg_before = stats.mean

        # Update stats with current transaction
        stats.update(amount)

        score = 0.0
        triggered = False
        if count_before >= min_txns and avg_before > 0:
            ratio = amount / (avg_before * multiplier)
            if ratio > 1.0:
                score = min(1.0, ratio - 1.0 + 0.5)
                triggered = True

        return FraudRuleResult(
            rule_id=FraudRuleId.HIGH_VALUE,
            score=score,
            triggered=triggered,
            details={"amount": amount, "customer_avg": avg_before, "count": count_before},
        )

    def _eval_velocity(self, customer_id: str, timestamp_epoch: float) -> FraudRuleResult:
        """FR-002: Velocity — too many transactions in time window."""
        cfg = self.config.get("velocity", {})
        max_count = cfg.get("max_count", 5)
        window_seconds = cfg.get("window_minutes", 10) * 60

        window = self._velocity_windows.setdefault(customer_id, [])
        window.append(timestamp_epoch)

        # Prune old entries
        cutoff = timestamp_epoch - window_seconds
        self._velocity_windows[customer_id] = [t for t in window if t > cutoff]
        window = self._velocity_windows[customer_id]

        count = len(window)
        score = 0.0
        triggered = False
        if count > max_count:
            score = min(1.0, (count - max_count) / max_count)
            triggered = True

        return FraudRuleResult(
            rule_id=FraudRuleId.VELOCITY,
            score=score,
            triggered=triggered,
            details={"count_in_window": count, "max_count": max_count},
        )

    def _eval_geographic(
        self,
        customer_id: str,
        latitude: float | None,
        longitude: float | None,
        timestamp_epoch: float,
    ) -> FraudRuleResult:
        """FR-003: Geographic — impossible travel detection."""
        cfg = self.config.get("geographic", {})
        max_distance = cfg.get("max_distance_km", 500)
        max_hours = cfg.get("max_time_hours", 1)

        score = 0.0
        triggered = False
        details: dict[str, object] = {}

        if latitude is not None and longitude is not None:
            last = self._last_locations.get(customer_id)
            if last is not None:
                distance = haversine_km(last.latitude, last.longitude, latitude, longitude)
                time_hours = (timestamp_epoch - last.timestamp_epoch) / 3600

                if time_hours > 0 and time_hours <= max_hours and distance > max_distance:
                    score = min(1.0, distance / (max_distance * 2))
                    triggered = True
                    details = {
                        "distance_km": round(distance, 1),
                        "time_hours": round(time_hours, 2),
                    }

            self._last_locations[customer_id] = GeoLocation(
                latitude=latitude,
                longitude=longitude,
                timestamp_epoch=timestamp_epoch,
            )

        return FraudRuleResult(
            rule_id=FraudRuleId.GEOGRAPHIC,
            score=score,
            triggered=triggered,
            details=details,
        )

    def _eval_time_anomaly(
        self, customer_id: str, timestamp_epoch: float
    ) -> FraudRuleResult:
        """FR-004: Time Anomaly — transaction at unusual hour."""
        cfg = self.config.get("time_anomaly", {})
        threshold = cfg.get("std_dev_threshold", 2.0)

        import datetime

        hour = datetime.datetime.fromtimestamp(timestamp_epoch).hour + (
            datetime.datetime.fromtimestamp(timestamp_epoch).minute / 60
        )

        stats = self._hour_stats.setdefault(customer_id, RunningStats())

        score = 0.0
        triggered = False
        if stats.count >= 5 and stats.std_dev > 0:
            z_score = abs(hour - stats.mean) / stats.std_dev
            if z_score > threshold:
                score = min(1.0, (z_score - threshold) / threshold)
                triggered = True

        stats.update(hour)

        return FraudRuleResult(
            rule_id=FraudRuleId.TIME_ANOMALY,
            score=score,
            triggered=triggered,
            details={"hour": round(hour, 1), "mean_hour": round(stats.mean, 1)},
        )

    def _eval_blacklist(
        self, customer_id: str, store_id: str | None
    ) -> FraudRuleResult:
        """FR-005: Blacklist — customer or store on known fraud list."""
        on_list = customer_id in self._blacklist
        if store_id and store_id in self._blacklist:
            on_list = True

        return FraudRuleResult(
            rule_id=FraudRuleId.BLACKLIST,
            score=1.0 if on_list else 0.0,
            triggered=on_list,
            details={"blacklisted": on_list},
        )

    @staticmethod
    def _rule_id_to_config_key(rule_id: str) -> str:
        """Map FraudRuleId to config dict key."""
        mapping = {
            "FR-001": "high_value",
            "FR-002": "velocity",
            "FR-003": "geographic",
            "FR-004": "time_anomaly",
            "FR-005": "blacklist",
        }
        return mapping.get(rule_id, "unknown")
