"""Integration tests for ML pipeline.

Tests verify the end-to-end flow:
  CustomerFraudState -> Feature Engineering -> Model Scoring -> Rule Integration
"""

from __future__ import annotations

import time

import pytest

from src.flink_jobs.common.state import CustomerFraudState
from src.flink_jobs.fraud_detector import FraudEngine, FraudRuleEvaluator
from src.flink_jobs.ml.feature_engineering import (
    FEATURE_NAMES,
    NUM_FEATURES,
    extract_features,
)
from src.generators.customer_generator import generate_customers
from src.generators.store_generator import generate_stores
from src.generators.transaction_generator import TransactionGenerator

pytestmark = pytest.mark.integration


def _sklearn_available() -> bool:
    try:
        import sklearn  # noqa: F401

        return True
    except ImportError:
        return False


class TestFeatureExtractionPipeline:
    """Test feature extraction with realistic data from generators."""

    def test_features_from_generated_transactions(self) -> None:
        customers = generate_customers(5, seed=42)
        stores = generate_stores(3, seed=42)
        generator = TransactionGenerator(customers=customers, stores=stores, seed=42)

        state = CustomerFraudState()
        evaluator = FraudRuleEvaluator()

        now = time.time()
        for i in range(20):
            txn = generator.generate()
            evaluator.evaluate(state, float(txn.amount), now + i * 300)

        features = extract_features(
            state=state,
            amount=999.99,
            hour=3.0,
            timestamp_epoch=now + 7000,
        )
        assert len(features) == NUM_FEATURES
        assert all(isinstance(f, float) for f in features)
        assert features[FEATURE_NAMES.index("velocity_count")] > 0
        assert features[FEATURE_NAMES.index("amount_ratio")] > 0

    def test_features_with_geographic_data(self) -> None:
        state = CustomerFraudState()
        evaluator = FraudRuleEvaluator()

        now = time.time()
        evaluator.evaluate(
            state,
            100.0,
            now,
            latitude=-23.55,
            longitude=-46.63,
        )

        features = extract_features(
            state=state,
            amount=200.0,
            hour=14.0,
            latitude=-22.90,
            longitude=-43.17,
            timestamp_epoch=now + 3600,
        )
        geo_speed = features[FEATURE_NAMES.index("geo_speed_kmh")]
        assert geo_speed > 0

    def test_features_for_blacklisted_customer(self) -> None:
        state = CustomerFraudState(blacklisted=True)
        features = extract_features(state=state, amount=100.0, hour=12.0)
        assert features[FEATURE_NAMES.index("is_blacklisted")] == 1.0

    def test_features_for_normal_customer(self) -> None:
        state = CustomerFraudState(blacklisted=False)
        features = extract_features(state=state, amount=100.0, hour=12.0)
        assert features[FEATURE_NAMES.index("is_blacklisted")] == 0.0


class TestMLScoringIntegration:
    """Test ML scoring with mocked model (no sklearn required for CI)."""

    def test_scorer_without_model_returns_zero(self) -> None:
        from src.flink_jobs.ml.model_scorer import AnomalyScorer

        scorer = AnomalyScorer(model_path="/nonexistent/path.joblib")
        scorer.load()
        assert not scorer.is_loaded
        assert scorer.score([0.0] * NUM_FEATURES) == 0.0

    @pytest.mark.skipif(
        not _sklearn_available(),
        reason="sklearn not installed",
    )
    def test_scorer_with_trained_model(self, tmp_path: object) -> None:
        import joblib
        import numpy as np
        from sklearn.ensemble import IsolationForest

        from src.flink_jobs.ml.model_scorer import AnomalyScorer

        rng = np.random.default_rng(42)
        data = rng.standard_normal((200, NUM_FEATURES))
        model = IsolationForest(n_estimators=50, random_state=42)
        model.fit(data)

        model_path = tmp_path / "test_model.joblib"  # type: ignore[operator]
        joblib.dump(model, model_path)

        scorer = AnomalyScorer(model_path=model_path)
        scorer.load()
        assert scorer.is_loaded

        normal_features = [0.0] * NUM_FEATURES
        score = scorer.score(normal_features)
        assert 0.0 <= score <= 1.0

        anomaly_features = [10.0, 50.0, 5.0, 1000.0, 1.0, 20.0]
        anomaly_score = scorer.score(anomaly_features)
        assert 0.0 <= anomaly_score <= 1.0


class TestFraudEngineWithMLFeatures:
    """Test FraudEngine produces state suitable for ML feature extraction."""

    def test_engine_state_feeds_feature_extraction(self) -> None:
        engine = FraudEngine()
        customer_id = "cust-ml-001"

        now = time.time()
        for i in range(10):
            engine.evaluate(customer_id, 100.0 + i * 10, now + i * 600)

        state = engine._get_state(customer_id)
        features = extract_features(
            state=state,
            amount=500.0,
            hour=3.0,
            timestamp_epoch=now + 7000,
        )
        assert len(features) == NUM_FEATURES
        assert features[FEATURE_NAMES.index("amount_ratio")] > 1.0

    def test_state_accumulation_across_transactions(self) -> None:
        engine = FraudEngine()
        customer_id = "cust-ml-002"

        now = time.time()
        for i in range(5):
            engine.evaluate(
                customer_id,
                50.0,
                now + i * 60,
                latitude=-23.55,
                longitude=-46.63,
            )

        state = engine._get_state(customer_id)
        assert state.amount_stats.count == 5
        assert state.velocity_window.count == 5
        assert state.last_location is not None
