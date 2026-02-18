"""Fraud rule evaluator — pure Python business logic for 5 fraud detection rules.

This module contains ONLY business logic with zero Flink dependencies.
State is received as parameters, not stored in instance dictionaries.
The Flink integration (KeyedProcessFunction, ValueState) lives in
fraud_detector_function.py.

Rules:
    FR-001: High Value — Transaction > multiplier * customer average
    FR-002: Velocity — Too many transactions in a time window
    FR-003: Geographic — Impossible travel detection
    FR-004: Time Anomaly — Transaction at unusual hour for customer
    FR-005: Blacklist — Customer/store on known fraud list
"""

from __future__ import annotations

import datetime
import logging
import time
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from src.flink_jobs.common.state import (
    CustomerFraudState,
    FraudRuleResult,
    GeoLocation,
    RunningStats,
    VelocityWindow,
    haversine_km,
)
from src.models.fraud_alert import FraudAlert, FraudRuleId

logger = logging.getLogger(__name__)

DEFAULT_RULES_CONFIG: dict[str, Any] = {
    "high_value": {"multiplier": 3.0, "min_transactions": 5, "weight": 0.30},
    "velocity": {"max_count": 5, "window_minutes": 10, "weight": 0.25},
    "geographic": {"max_distance_km": 500, "max_time_hours": 1, "weight": 0.20},
    "time_anomaly": {"std_dev_threshold": 2.0, "weight": 0.15},
    "blacklist": {"weight": 0.10},
}

ALERT_THRESHOLD = 0.7


class FraudRuleEvaluator:
    """Stateless fraud rule evaluator.

    All per-customer state is passed in via CustomerFraudState parameter.
    This separation enables:
    - Pure unit testing without Flink runtime
    - Flink KeyedProcessFunction to manage state lifecycle
    - Reuse in batch (Airflow) and streaming (Flink) contexts
    """

    def __init__(self, rules_config: dict[str, Any] | None = None) -> None:
        self.config = rules_config or DEFAULT_RULES_CONFIG
        self.threshold: float = float(self.config.get("alert_threshold", ALERT_THRESHOLD))

    def evaluate(
        self,
        state: CustomerFraudState,
        amount: float,
        timestamp_epoch: float,
        latitude: float | None = None,
        longitude: float | None = None,
        store_id: str | None = None,
    ) -> tuple[float, list[FraudRuleResult]]:
        """Evaluate all fraud rules against customer state.

        State is mutated in-place (caller is responsible for persisting it).

        Returns:
            Tuple of (weighted_score, list of rule results).
        """
        results: list[FraudRuleResult] = [
            self._eval_high_value(state.amount_stats, amount),
            self._eval_velocity(state.velocity_window, timestamp_epoch),
            self._eval_geographic(state.last_location, latitude, longitude, timestamp_epoch),
            self._eval_time_anomaly(state.hour_stats, timestamp_epoch),
            self._eval_blacklist(state.blacklisted, store_id),
        ]

        # Update location state after evaluation
        if latitude is not None and longitude is not None:
            state.last_location = GeoLocation(
                latitude=latitude,
                longitude=longitude,
                timestamp_epoch=timestamp_epoch,
            )

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

    def build_alert(
        self,
        transaction_data: dict[str, Any],
        score: float,
        results: list[FraudRuleResult],
    ) -> FraudAlert | None:
        """Build FraudAlert if score exceeds threshold."""
        if score < self.threshold:
            return None

        triggered_rules = [FraudRuleId(r.rule_id) for r in results if r.triggered]
        rule_details: dict[str, object] = {r.rule_id: asdict(r) for r in results if r.triggered}

        return FraudAlert(
            transaction_id=transaction_data["transaction_id"],
            customer_id=transaction_data["customer_id"],
            fraud_score=Decimal(str(round(score, 3))),
            rules_triggered=triggered_rules,
            rule_details=rule_details,
            transaction_amount=Decimal(str(transaction_data["amount"])),
        )

    # --- Individual Rules (pure functions operating on state objects) ---

    def _eval_high_value(self, amount_stats: RunningStats, amount: float) -> FraudRuleResult:
        """FR-001: High Value — transaction > multiplier * customer average."""
        cfg = self.config.get("high_value", {})
        multiplier = cfg.get("multiplier", 3.0)
        min_txns = cfg.get("min_transactions", 5)

        count_before = amount_stats.count
        avg_before = amount_stats.mean

        amount_stats.update(amount)

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

    def _eval_velocity(
        self, velocity_window: VelocityWindow, timestamp_epoch: float
    ) -> FraudRuleResult:
        """FR-002: Velocity — too many transactions in time window."""
        cfg = self.config.get("velocity", {})
        max_count = cfg.get("max_count", 5)
        window_seconds = cfg.get("window_minutes", 10) * 60

        velocity_window.add(timestamp_epoch)
        velocity_window.prune(timestamp_epoch - window_seconds)

        count = velocity_window.count
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
        last_location: GeoLocation | None,
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

        if latitude is not None and longitude is not None and last_location is not None:
            distance = haversine_km(
                last_location.latitude, last_location.longitude, latitude, longitude
            )
            time_hours = (timestamp_epoch - last_location.timestamp_epoch) / 3600

            if time_hours > 0 and time_hours <= max_hours and distance > max_distance:
                score = min(1.0, distance / (max_distance * 2))
                triggered = True
                details = {
                    "distance_km": round(distance, 1),
                    "time_hours": round(time_hours, 2),
                }

        return FraudRuleResult(
            rule_id=FraudRuleId.GEOGRAPHIC,
            score=score,
            triggered=triggered,
            details=details,
        )

    def _eval_time_anomaly(
        self, hour_stats: RunningStats, timestamp_epoch: float
    ) -> FraudRuleResult:
        """FR-004: Time Anomaly — transaction at unusual hour."""
        cfg = self.config.get("time_anomaly", {})
        threshold = cfg.get("std_dev_threshold", 2.0)

        dt = datetime.datetime.fromtimestamp(timestamp_epoch)
        hour = dt.hour + (dt.minute / 60)

        score = 0.0
        triggered = False
        if hour_stats.count >= 5 and hour_stats.std_dev > 0:
            z_score = abs(hour - hour_stats.mean) / hour_stats.std_dev
            if z_score > threshold:
                score = min(1.0, (z_score - threshold) / threshold)
                triggered = True

        hour_stats.update(hour)

        return FraudRuleResult(
            rule_id=FraudRuleId.TIME_ANOMALY,
            score=score,
            triggered=triggered,
            details={"hour": round(hour, 1), "mean_hour": round(hour_stats.mean, 1)},
        )

    @staticmethod
    def _eval_blacklist(is_blacklisted: bool, store_id: str | None) -> FraudRuleResult:
        """FR-005: Blacklist — customer or store on known fraud list."""
        _ = store_id  # Store-level blacklist handled at state loading
        return FraudRuleResult(
            rule_id=FraudRuleId.BLACKLIST,
            score=1.0 if is_blacklisted else 0.0,
            triggered=is_blacklisted,
            details={"blacklisted": is_blacklisted},
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
            "FR-006": "ml_anomaly",
        }
        return mapping.get(rule_id, "unknown")


class FraudEngine:
    """Backward-compatible wrapper around FraudRuleEvaluator.

    Maintains per-customer state in-memory dictionaries (legacy behavior).
    Used by existing tests and standalone evaluation. For Flink production
    use, see FraudDetectorFunction in fraud_detector_function.py.
    """

    def __init__(self, rules_config: dict[str, Any] | None = None) -> None:
        self._evaluator = FraudRuleEvaluator(rules_config)
        self._states: dict[str, CustomerFraudState] = {}
        self._blacklist: set[str] = set()

    @property
    def config(self) -> dict[str, Any]:
        return self._evaluator.config

    @property
    def threshold(self) -> float:
        return self._evaluator.threshold

    def set_blacklist(self, blacklisted_ids: set[str]) -> None:
        """Update the blacklist (called via broadcast state in Flink)."""
        self._blacklist = blacklisted_ids

    def _get_state(self, customer_id: str) -> CustomerFraudState:
        if customer_id not in self._states:
            self._states[customer_id] = CustomerFraudState()
        state = self._states[customer_id]
        state.blacklisted = customer_id in self._blacklist
        return state

    def evaluate(
        self,
        customer_id: str,
        amount: float,
        timestamp_epoch: float,
        latitude: float | None = None,
        longitude: float | None = None,
        store_id: str | None = None,
    ) -> tuple[float, list[FraudRuleResult]]:
        """Evaluate all fraud rules for a transaction."""
        state = self._get_state(customer_id)
        if store_id and store_id in self._blacklist:
            state.blacklisted = True
        return self._evaluator.evaluate(
            state=state,
            amount=amount,
            timestamp_epoch=timestamp_epoch,
            latitude=latitude,
            longitude=longitude,
            store_id=store_id,
        )

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

        return self._evaluator.build_alert(transaction_data, score, results)
