"""Flink KeyedProcessFunction for real-time fraud detection.

Wraps FraudRuleEvaluator with fault-tolerant Flink state management:
- ValueState[bytes] for RunningStats (amount, hour), GeoLocation
- ListState[bytes] for VelocityWindow timestamps
- OutputTag for fraud alert side output

State survives restarts via RocksDB checkpointing + savepoints.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any

from pyflink.common import Types
from pyflink.datastream import OutputTag, RuntimeContext
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.datastream.state import ListStateDescriptor, ValueStateDescriptor

from src.flink_jobs.common.state import (
    CustomerFraudState,
    GeoLocation,
    RunningStats,
    VelocityWindow,
)
from src.flink_jobs.fraud_detector import FraudRuleEvaluator

logger = logging.getLogger(__name__)

FRAUD_ALERT_TAG = OutputTag("fraud-alerts", Types.STRING())


class FraudDetectorFunction(KeyedProcessFunction):  # type: ignore[misc]
    """Keyed process function for per-customer fraud detection.

    State layout (keyed by customer_id):
        amount_stats:    ValueState[bytes] — RunningStats for transaction amounts
        hour_stats:      ValueState[bytes] — RunningStats for transaction hours
        last_location:   ValueState[bytes] — GeoLocation of last transaction
        velocity_window: ListState[bytes]  — timestamps in sliding window
        blacklisted:     ValueState[bytes] — JSON bool flag

    On each element:
        1. Deserialize per-customer state from ValueState/ListState
        2. Build CustomerFraudState dataclass
        3. Call FraudRuleEvaluator.evaluate() (pure Python, no Flink deps)
        4. Persist updated state back to ValueState/ListState
        5. Emit fraud alerts via side output if threshold exceeded
    """

    def __init__(self, rules_config: dict[str, Any] | None = None) -> None:
        self._rules_config = rules_config
        self._evaluator: FraudRuleEvaluator | None = None

    def open(self, runtime_context: RuntimeContext) -> None:
        self._evaluator = FraudRuleEvaluator(self._rules_config)

        self._amount_stats_state = runtime_context.get_state(
            ValueStateDescriptor("amount_stats", Types.PICKLED_BYTE_ARRAY())
        )
        self._hour_stats_state = runtime_context.get_state(
            ValueStateDescriptor("hour_stats", Types.PICKLED_BYTE_ARRAY())
        )
        self._last_location_state = runtime_context.get_state(
            ValueStateDescriptor("last_location", Types.PICKLED_BYTE_ARRAY())
        )
        self._velocity_state = runtime_context.get_list_state(
            ListStateDescriptor("velocity_window", Types.PICKLED_BYTE_ARRAY())
        )
        self._blacklisted_state = runtime_context.get_state(
            ValueStateDescriptor("blacklisted", Types.PICKLED_BYTE_ARRAY())
        )

    def process_element(self, value: str, ctx: KeyedProcessFunction.Context) -> None:
        assert self._evaluator is not None

        try:
            txn_data: dict[str, Any] = json.loads(value)
        except json.JSONDecodeError:
            logger.warning("Malformed JSON in fraud detector: %s", value[:200])
            return

        customer_id = txn_data.get("customer_id", "")
        amount = float(txn_data.get("amount", 0))
        timestamp_epoch = txn_data.get("timestamp_epoch", time.time())

        state = self._load_state()

        score, results = self._evaluator.evaluate(
            state=state,
            amount=amount,
            timestamp_epoch=timestamp_epoch,
            latitude=txn_data.get("latitude"),
            longitude=txn_data.get("longitude"),
            store_id=txn_data.get("store_id"),
        )

        self._persist_state(state)

        alert = self._evaluator.build_alert(txn_data, score, results)
        if alert is not None:
            ctx.output(FRAUD_ALERT_TAG, json.dumps(alert.to_json_dict(), default=str))
            logger.info(
                "Fraud alert emitted for customer=%s score=%.3f",
                customer_id,
                score,
            )

    def _load_state(self) -> CustomerFraudState:
        amount_bytes = self._amount_stats_state.value()
        amount_stats = RunningStats.from_bytes(amount_bytes) if amount_bytes else RunningStats()

        hour_bytes = self._hour_stats_state.value()
        hour_stats = RunningStats.from_bytes(hour_bytes) if hour_bytes else RunningStats()

        loc_bytes = self._last_location_state.value()
        last_location = GeoLocation.from_bytes(loc_bytes) if loc_bytes else None

        timestamps: list[float] = []
        for entry in self._velocity_state.get():
            ts_list: list[float] = json.loads(entry)
            timestamps.extend(ts_list)
        velocity_window = VelocityWindow(timestamps=timestamps)

        bl_bytes = self._blacklisted_state.value()
        blacklisted = json.loads(bl_bytes) if bl_bytes else False

        return CustomerFraudState(
            amount_stats=amount_stats,
            hour_stats=hour_stats,
            velocity_window=velocity_window,
            last_location=last_location,
            blacklisted=blacklisted,
        )

    def _persist_state(self, state: CustomerFraudState) -> None:
        self._amount_stats_state.update(state.amount_stats.to_bytes())
        self._hour_stats_state.update(state.hour_stats.to_bytes())

        if state.last_location is not None:
            self._last_location_state.update(state.last_location.to_bytes())

        self._velocity_state.clear()
        if state.velocity_window.timestamps:
            self._velocity_state.add(state.velocity_window.to_bytes())

        self._blacklisted_state.update(json.dumps(state.blacklisted).encode("utf-8"))
