"""Unit tests for fraud detection engine."""

from __future__ import annotations

import time

from src.flink_jobs.fraud_detector import FraudEngine


class TestHighValueRule:
    """Tests for FR-001: High Value detection."""

    def test_normal_transaction_no_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-hv-001"
        # Build history: 10 transactions at ~100
        for _ in range(10):
            engine.evaluate(cid, 100.0, time.time())
        # Transaction at 200 (2x avg, below 3x multiplier)
        _score, results = engine.evaluate(cid, 200.0, time.time())
        hv = next(r for r in results if r.rule_id == "FR-001")
        assert not hv.triggered

    def test_high_value_triggers_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-hv-002"
        for _ in range(10):
            engine.evaluate(cid, 100.0, time.time())
        # Transaction at 500 (5x avg, above 3x multiplier)
        _score, results = engine.evaluate(cid, 500.0, time.time())
        hv = next(r for r in results if r.rule_id == "FR-001")
        assert hv.triggered
        assert hv.score > 0.0

    def test_insufficient_history_no_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-hv-003"
        # Only 3 transactions (below min_transactions=5)
        for _ in range(3):
            engine.evaluate(cid, 100.0, time.time())
        _score, results = engine.evaluate(cid, 9999.0, time.time())
        hv = next(r for r in results if r.rule_id == "FR-001")
        assert not hv.triggered


class TestVelocityRule:
    """Tests for FR-002: Velocity detection."""

    def test_normal_rate_no_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-vel-001"
        now = time.time()
        # 3 transactions in 10 minutes (below max_count=5)
        for i in range(3):
            engine.evaluate(cid, 100.0, now + i * 60)
        _, results = engine.evaluate(cid, 100.0, now + 300)
        vel = next(r for r in results if r.rule_id == "FR-002")
        assert not vel.triggered

    def test_high_velocity_triggers(self) -> None:
        engine = FraudEngine()
        cid = "cust-vel-002"
        now = time.time()
        # 8 transactions in 2 minutes (well above max_count=5 in 10min)
        for i in range(8):
            engine.evaluate(cid, 100.0, now + i * 15)
        _, results = engine.evaluate(cid, 100.0, now + 120)
        vel = next(r for r in results if r.rule_id == "FR-002")
        assert vel.triggered
        assert vel.score > 0.0


class TestGeographicRule:
    """Tests for FR-003: Geographic anomaly."""

    def test_nearby_transactions_no_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-geo-001"
        now = time.time()
        # São Paulo
        engine.evaluate(cid, 100.0, now, latitude=-23.55, longitude=-46.63)
        # São Paulo still (same city, minutes later)
        _, results = engine.evaluate(
            cid, 100.0, now + 600, latitude=-23.56, longitude=-46.64
        )
        geo = next(r for r in results if r.rule_id == "FR-003")
        assert not geo.triggered

    def test_impossible_travel_triggers(self) -> None:
        engine = FraudEngine()
        cid = "cust-geo-002"
        now = time.time()
        # São Paulo
        engine.evaluate(cid, 100.0, now, latitude=-23.55, longitude=-46.63)
        # Manaus, 30 minutes later (~2700km away)
        _, results = engine.evaluate(
            cid, 100.0, now + 1800, latitude=-3.12, longitude=-60.02
        )
        geo = next(r for r in results if r.rule_id == "FR-003")
        assert geo.triggered

    def test_no_location_no_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-geo-003"
        _, results = engine.evaluate(cid, 100.0, time.time())
        geo = next(r for r in results if r.rule_id == "FR-003")
        assert not geo.triggered


class TestTimeAnomalyRule:
    """Tests for FR-004: Time anomaly."""

    def test_consistent_hour_no_alert(self) -> None:
        engine = FraudEngine()
        cid = "cust-time-001"
        # All transactions at ~14:00 (2PM)
        base = 1704110400  # Some epoch at 14:00
        for i in range(10):
            engine.evaluate(cid, 100.0, base + i * 86400)
        _, results = engine.evaluate(cid, 100.0, base + 10 * 86400)
        ta = next(r for r in results if r.rule_id == "FR-004")
        assert not ta.triggered


class TestBlacklistRule:
    """Tests for FR-005: Blacklist."""

    def test_not_blacklisted_no_alert(self) -> None:
        engine = FraudEngine()
        _, results = engine.evaluate("cust-clean-001", 100.0, time.time())
        bl = next(r for r in results if r.rule_id == "FR-005")
        assert not bl.triggered

    def test_blacklisted_customer_triggers(self) -> None:
        engine = FraudEngine()
        engine.set_blacklist({"cust-bad-001"})
        _, results = engine.evaluate("cust-bad-001", 100.0, time.time())
        bl = next(r for r in results if r.rule_id == "FR-005")
        assert bl.triggered
        assert bl.score == 1.0

    def test_blacklisted_store_triggers(self) -> None:
        engine = FraudEngine()
        engine.set_blacklist({"store-bad-001"})
        _, results = engine.evaluate(
            "cust-clean-002", 100.0, time.time(), store_id="store-bad-001"
        )
        bl = next(r for r in results if r.rule_id == "FR-005")
        assert bl.triggered


class TestFraudEngineIntegration:
    """Integration tests for the full engine."""

    def test_process_transaction_below_threshold(self) -> None:
        engine = FraudEngine()
        data = {
            "transaction_id": "txn-int-001",
            "customer_id": "cust-int-001",
            "store_id": "store-001",
            "amount": 100.0,
            "timestamp_epoch": time.time(),
        }
        alert = engine.process_transaction(data)
        assert alert is None

    def test_process_transaction_blacklisted_triggers(self) -> None:
        engine = FraudEngine()
        engine.set_blacklist({"cust-bad-int"})
        # Build history for high value
        now = time.time()
        for i in range(10):
            engine.evaluate("cust-bad-int", 50.0, now + i * 60)
        # Now trigger multiple rules: high value + blacklist + velocity
        for i in range(8):
            data = {
                "transaction_id": f"txn-int-{i}",
                "customer_id": "cust-bad-int",
                "store_id": "store-001",
                "amount": 500.0,
                "timestamp_epoch": now + 600 + i * 10,
            }
            alert = engine.process_transaction(data)
        # 8 rapid high-value txns for a blacklisted customer should trigger
        # at least blacklist (FR-005) and velocity (FR-002) rules
        assert alert is not None
        assert alert.fraud_score > 0
        assert len(alert.rules_triggered) >= 1
