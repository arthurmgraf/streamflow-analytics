"""Unit tests for ML model scorer."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from src.flink_jobs.ml.model_scorer import AnomalyScorer


class TestAnomalyScorerWithoutModel:
    """Tests when model file is missing or not loaded."""

    def test_score_returns_zero_when_not_loaded(self) -> None:
        scorer = AnomalyScorer(model_path="nonexistent/model.joblib")
        # Don't call load(), model is None
        assert scorer.score([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) == 0.0

    def test_is_loaded_false_by_default(self) -> None:
        scorer = AnomalyScorer()
        assert not scorer.is_loaded

    def test_load_missing_file_disables_scoring(self) -> None:
        scorer = AnomalyScorer(model_path="nonexistent/model.joblib")
        scorer.load()
        assert not scorer.is_loaded
        assert scorer.score([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]) == 0.0


sklearn = pytest.importorskip("sklearn")
joblib = pytest.importorskip("joblib")
np = pytest.importorskip("numpy")


class TestAnomalyScorerWithModel:
    """Tests with a real (small) Isolation Forest model."""

    @pytest.fixture()
    def trained_scorer(self) -> AnomalyScorer:
        """Train a tiny model and save it to a temp file."""
        from sklearn.ensemble import IsolationForest

        rng = np.random.RandomState(42)
        normal_data = rng.randn(200, 6) * 0.5 + 5
        anomaly_data = rng.randn(10, 6) * 3 + 15
        data = np.vstack([normal_data, anomaly_data])

        model = IsolationForest(n_estimators=50, contamination=0.05, random_state=42)
        model.fit(data)

        with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as f:
            model_path = Path(f.name)
            joblib.dump(model, model_path)

        scorer = AnomalyScorer(
            model_path=model_path,
            score_min=-0.5,
            score_max=0.5,
        )
        scorer.load()
        return scorer

    def test_model_is_loaded(self, trained_scorer: AnomalyScorer) -> None:
        assert trained_scorer.is_loaded

    def test_score_in_valid_range(self, trained_scorer: AnomalyScorer) -> None:
        score = trained_scorer.score([5.0, 5.0, 5.0, 5.0, 5.0, 5.0])
        assert 0.0 <= score <= 1.0

    def test_normal_point_low_score(self, trained_scorer: AnomalyScorer) -> None:
        score = trained_scorer.score([5.0, 5.0, 5.0, 5.0, 5.0, 5.0])
        assert score < 0.7  # Normal data should have low anomaly score

    def test_anomalous_point_higher_score(self, trained_scorer: AnomalyScorer) -> None:
        normal_score = trained_scorer.score([5.0, 5.0, 5.0, 5.0, 5.0, 5.0])
        anomaly_score = trained_scorer.score([20.0, 20.0, 20.0, 20.0, 20.0, 20.0])
        assert anomaly_score > normal_score

    def test_multiple_scores_consistent(self, trained_scorer: AnomalyScorer) -> None:
        features = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0]
        score1 = trained_scorer.score(features)
        score2 = trained_scorer.score(features)
        assert abs(score1 - score2) < 1e-9  # Deterministic
