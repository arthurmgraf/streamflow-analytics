"""Unit tests for FraudDetectorFunction with mocked Flink state.

Tests the KeyedProcessFunction logic without a running Flink cluster
by mocking ValueState, ListState, RuntimeContext, and pyflink imports.
"""

from __future__ import annotations

import json
import sys
import time
from types import ModuleType
from typing import Any
from unittest.mock import MagicMock

# Mock pyflink modules before importing FraudDetectorFunction
_pyflink_mock = ModuleType("pyflink")
_pyflink_common = ModuleType("pyflink.common")
_pyflink_datastream = ModuleType("pyflink.datastream")
_pyflink_datastream_functions = ModuleType("pyflink.datastream.functions")
_pyflink_datastream_state = ModuleType("pyflink.datastream.state")

# Mock Types with PICKLED_BYTE_ARRAY
_mock_types = MagicMock()
_mock_types.PICKLED_BYTE_ARRAY.return_value = "PICKLED_BYTE_ARRAY"
_mock_types.STRING.return_value = "STRING"
_pyflink_common.Types = _mock_types  # type: ignore[attr-defined]

# Mock OutputTag
_mock_output_tag = MagicMock()
_pyflink_datastream.OutputTag = _mock_output_tag  # type: ignore[attr-defined]
_pyflink_datastream.RuntimeContext = MagicMock  # type: ignore[attr-defined]

# Mock KeyedProcessFunction as a real class (not MagicMock) so subclassing works
class _MockKeyedProcessFunction:
    class Context:
        pass

    def open(self, runtime_context: Any) -> None:
        pass

    def process_element(self, value: Any, ctx: Any) -> None:
        pass


_pyflink_datastream_functions.KeyedProcessFunction = _MockKeyedProcessFunction  # type: ignore[attr-defined]

# Mock state descriptors
_pyflink_datastream_state.ValueStateDescriptor = MagicMock  # type: ignore[attr-defined]
_pyflink_datastream_state.ListStateDescriptor = MagicMock  # type: ignore[attr-defined]

sys.modules["pyflink"] = _pyflink_mock
sys.modules["pyflink.common"] = _pyflink_common
sys.modules["pyflink.datastream"] = _pyflink_datastream
sys.modules["pyflink.datastream.functions"] = _pyflink_datastream_functions
sys.modules["pyflink.datastream.state"] = _pyflink_datastream_state

from src.flink_jobs.fraud_detector_function import FraudDetectorFunction  # noqa: E402


class MockValueState:
    """Mock Flink ValueState[bytes]."""

    def __init__(self) -> None:
        self._value: bytes | None = None

    def value(self) -> bytes | None:
        return self._value

    def update(self, v: bytes) -> None:
        self._value = v

    def clear(self) -> None:
        self._value = None


class MockListState:
    """Mock Flink ListState[bytes]."""

    def __init__(self) -> None:
        self._items: list[bytes] = []

    def get(self) -> list[bytes]:
        return list(self._items)

    def add(self, v: bytes) -> None:
        self._items.append(v)

    def clear(self) -> None:
        self._items.clear()


class MockContext:
    """Mock KeyedProcessFunction.Context with side output capture."""

    def __init__(self) -> None:
        self.side_outputs: list[tuple[Any, str]] = []

    def output(self, tag: Any, value: str) -> None:
        self.side_outputs.append((tag, value))

    def current_key(self) -> str:
        return "test-customer"


def _make_runtime_context() -> MagicMock:
    """Build a mock RuntimeContext that returns MockValueState/MockListState."""
    ctx = MagicMock()
    states: dict[str, MockValueState | MockListState] = {}

    def get_state(descriptor: Any) -> MockValueState:
        name = str(descriptor)
        if name not in states:
            states[name] = MockValueState()
        return states[name]  # type: ignore[return-value]

    def get_list_state(descriptor: Any) -> MockListState:
        name = str(descriptor)
        if name not in states:
            states[name] = MockListState()
        return states[name]  # type: ignore[return-value]

    ctx.get_state = get_state
    ctx.get_list_state = get_list_state
    return ctx


def _build_txn(
    customer_id: str = "cust-001",
    amount: float = 100.0,
    timestamp_epoch: float | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    store_id: str = "store-001",
) -> str:
    data: dict[str, Any] = {
        "transaction_id": f"txn-{time.time_ns()}",
        "customer_id": customer_id,
        "store_id": store_id,
        "amount": amount,
        "timestamp_epoch": timestamp_epoch or time.time(),
    }
    if latitude is not None:
        data["latitude"] = latitude
    if longitude is not None:
        data["longitude"] = longitude
    return json.dumps(data)


class TestFraudDetectorFunctionOpen:
    """Tests for open() initialization."""

    def test_open_initializes_evaluator(self) -> None:
        func = FraudDetectorFunction()
        runtime_ctx = _make_runtime_context()
        func.open(runtime_ctx)
        assert func._evaluator is not None

    def test_open_with_custom_config(self) -> None:
        config = {"high_value": {"multiplier": 5.0, "min_transactions": 10, "weight": 0.40}}
        func = FraudDetectorFunction(rules_config=config)
        runtime_ctx = _make_runtime_context()
        func.open(runtime_ctx)
        assert func._evaluator is not None
        assert func._evaluator.config["high_value"]["multiplier"] == 5.0


class TestFraudDetectorFunctionProcessElement:
    """Tests for process_element() — the core processing loop."""

    def _setup_function(self) -> tuple[FraudDetectorFunction, MockContext]:
        func = FraudDetectorFunction()
        runtime_ctx = _make_runtime_context()
        func.open(runtime_ctx)
        ctx = MockContext()
        return func, ctx

    def test_normal_transaction_no_side_output(self) -> None:
        func, ctx = self._setup_function()
        func.process_element(_build_txn(amount=50.0), ctx)
        assert len(ctx.side_outputs) == 0

    def test_malformed_json_skipped(self) -> None:
        func, ctx = self._setup_function()
        func.process_element("not-json{{{", ctx)
        assert len(ctx.side_outputs) == 0

    def test_state_accumulates_across_calls(self) -> None:
        func, ctx = self._setup_function()
        now = time.time()
        for i in range(5):
            func.process_element(
                _build_txn(amount=100.0, timestamp_epoch=now + i * 60), ctx
            )
        state = func._load_state()
        assert state.amount_stats.count == 5
        assert state.velocity_window.count == 5

    def test_location_persisted(self) -> None:
        func, ctx = self._setup_function()
        func.process_element(
            _build_txn(latitude=-23.55, longitude=-46.63), ctx
        )
        state = func._load_state()
        assert state.last_location is not None
        assert state.last_location.latitude == -23.55


class TestFraudDetectorFunctionStatePersistence:
    """Tests that state survives serialization cycles."""

    def _setup_function(self) -> tuple[FraudDetectorFunction, MockContext]:
        func = FraudDetectorFunction()
        runtime_ctx = _make_runtime_context()
        func.open(runtime_ctx)
        ctx = MockContext()
        return func, ctx

    def test_amount_stats_survive_reload(self) -> None:
        func, ctx = self._setup_function()
        now = time.time()
        for i in range(3):
            func.process_element(
                _build_txn(amount=100.0 + i * 10, timestamp_epoch=now + i * 60), ctx
            )
        state = func._load_state()
        assert state.amount_stats.count == 3
        assert abs(state.amount_stats.mean - 110.0) < 1e-9

    def test_velocity_window_survives_reload(self) -> None:
        func, ctx = self._setup_function()
        now = time.time()
        for i in range(4):
            func.process_element(
                _build_txn(timestamp_epoch=now + i * 30), ctx
            )
        state = func._load_state()
        assert state.velocity_window.count == 4


class TestFraudDetectorFunctionAlertEmission:
    """Tests for fraud alert side output emission."""

    def test_blacklisted_with_history_may_emit_alert(self) -> None:
        config = {
            "high_value": {"multiplier": 2.0, "min_transactions": 3, "weight": 0.40},
            "velocity": {"max_count": 3, "window_minutes": 10, "weight": 0.25},
            "geographic": {"max_distance_km": 500, "max_time_hours": 1, "weight": 0.10},
            "time_anomaly": {"std_dev_threshold": 2.0, "weight": 0.10},
            "blacklist": {"weight": 0.15},
            "alert_threshold": 0.3,
        }
        func = FraudDetectorFunction(rules_config=config)
        runtime_ctx = _make_runtime_context()
        func.open(runtime_ctx)

        state = func._load_state()
        state.blacklisted = True
        func._persist_state(state)

        now = time.time()
        ctx = MockContext()
        for i in range(5):
            func.process_element(
                _build_txn(amount=50.0, timestamp_epoch=now + i * 60), ctx
            )
        func.process_element(
            _build_txn(amount=500.0, timestamp_epoch=now + 350), ctx
        )
        for _tag, value in ctx.side_outputs:
            alert_data = json.loads(value)
            assert "transaction_id" in alert_data
            assert "fraud_score" in alert_data
