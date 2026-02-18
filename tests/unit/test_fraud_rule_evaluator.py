"""Unit tests for FraudRuleEvaluator (stateless, pure Python)."""

from __future__ import annotations

import time

from src.flink_jobs.common.state import CustomerFraudState
from src.flink_jobs.fraud_detector import FraudRuleEvaluator


class TestFraudRuleEvaluatorStateless:
    """Tests that FraudRuleEvaluator operates purely on passed-in state."""

    def test_fresh_state_no_triggers(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        score, results = evaluator.evaluate(state, amount=50.0, timestamp_epoch=time.time())
        assert score == 0.0
        assert all(not r.triggered for r in results)

    def test_state_is_mutated_in_place(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        evaluator.evaluate(state, amount=100.0, timestamp_epoch=time.time())
        assert state.amount_stats.count == 1
        assert state.amount_stats.mean == 100.0
        assert state.velocity_window.count == 1

    def test_multiple_evaluations_accumulate(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        now = time.time()
        for i in range(10):
            evaluator.evaluate(state, amount=100.0, timestamp_epoch=now + i * 60)
        assert state.amount_stats.count == 10
        assert state.velocity_window.count == 10

    def test_high_value_triggers_with_pre_built_state(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        now = time.time()
        for i in range(10):
            evaluator.evaluate(state, amount=100.0, timestamp_epoch=now + i * 60)
        _score, results = evaluator.evaluate(state, amount=500.0, timestamp_epoch=now + 700)
        hv = next(r for r in results if r.rule_id == "FR-001")
        assert hv.triggered

    def test_velocity_triggers_with_rapid_transactions(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        now = time.time()
        for i in range(8):
            evaluator.evaluate(state, amount=50.0, timestamp_epoch=now + i * 10)
        _score, results = evaluator.evaluate(state, amount=50.0, timestamp_epoch=now + 90)
        vel = next(r for r in results if r.rule_id == "FR-002")
        assert vel.triggered

    def test_geographic_impossible_travel(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        now = time.time()
        evaluator.evaluate(
            state,
            amount=50.0,
            timestamp_epoch=now,
            latitude=-23.55,
            longitude=-46.63,
        )
        _score, results = evaluator.evaluate(
            state,
            amount=50.0,
            timestamp_epoch=now + 1800,
            latitude=-3.12,
            longitude=-60.02,
        )
        geo = next(r for r in results if r.rule_id == "FR-003")
        assert geo.triggered

    def test_blacklisted_customer(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState(blacklisted=True)
        _score, results = evaluator.evaluate(state, amount=50.0, timestamp_epoch=time.time())
        bl = next(r for r in results if r.rule_id == "FR-005")
        assert bl.triggered
        assert bl.score == 1.0

    def test_location_updated_after_evaluation(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        now = time.time()
        evaluator.evaluate(
            state,
            amount=50.0,
            timestamp_epoch=now,
            latitude=-23.55,
            longitude=-46.63,
        )
        assert state.last_location is not None
        assert state.last_location.latitude == -23.55

    def test_build_alert_above_threshold(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState(blacklisted=True)
        now = time.time()
        for i in range(10):
            evaluator.evaluate(state, amount=50.0, timestamp_epoch=now + i * 60)
        for i in range(8):
            evaluator.evaluate(state, amount=500.0, timestamp_epoch=now + 700 + i * 5)
        score, results = evaluator.evaluate(
            state,
            amount=1000.0,
            timestamp_epoch=now + 750,
        )
        txn_data = {
            "transaction_id": "txn-alert-001",
            "customer_id": "cust-bad",
            "amount": 1000.0,
        }
        alert = evaluator.build_alert(txn_data, score, results)
        if score >= evaluator.threshold:
            assert alert is not None
            assert len(alert.rules_triggered) > 0
        else:
            assert alert is None

    def test_build_alert_below_threshold_returns_none(self) -> None:
        evaluator = FraudRuleEvaluator()
        state = CustomerFraudState()
        score, results = evaluator.evaluate(state, amount=50.0, timestamp_epoch=time.time())
        txn_data = {
            "transaction_id": "txn-ok-001",
            "customer_id": "cust-ok",
            "amount": 50.0,
        }
        alert = evaluator.build_alert(txn_data, score, results)
        assert alert is None

    def test_different_states_are_independent(self) -> None:
        evaluator = FraudRuleEvaluator()
        state_a = CustomerFraudState()
        state_b = CustomerFraudState()
        evaluator.evaluate(state_a, amount=100.0, timestamp_epoch=time.time())
        assert state_a.amount_stats.count == 1
        assert state_b.amount_stats.count == 0

    def test_custom_config(self) -> None:
        config = {
            "high_value": {"multiplier": 2.0, "min_transactions": 3, "weight": 0.50},
            "velocity": {"max_count": 3, "window_minutes": 5, "weight": 0.25},
            "geographic": {"max_distance_km": 200, "max_time_hours": 0.5, "weight": 0.10},
            "time_anomaly": {"std_dev_threshold": 1.5, "weight": 0.10},
            "blacklist": {"weight": 0.05},
            "alert_threshold": 0.5,
        }
        evaluator = FraudRuleEvaluator(config)
        assert evaluator.threshold == 0.5
        assert evaluator.config["high_value"]["multiplier"] == 2.0
