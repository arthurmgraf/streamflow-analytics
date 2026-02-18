"""Unit tests for ML feature engineering."""

from __future__ import annotations

from src.flink_jobs.common.state import CustomerFraudState, GeoLocation
from src.flink_jobs.ml.feature_engineering import (
    FEATURE_NAMES,
    NUM_FEATURES,
    extract_features,
)


class TestExtractFeatures:
    """Tests for feature vector extraction."""

    def test_output_length(self) -> None:
        state = CustomerFraudState()
        features = extract_features(state, amount=100.0, hour=14.0)
        assert len(features) == NUM_FEATURES
        assert len(features) == len(FEATURE_NAMES)

    def test_fresh_state_returns_zeros(self) -> None:
        state = CustomerFraudState()
        features = extract_features(state, amount=100.0, hour=14.0)
        assert features[0] == 0.0  # amount_zscore (no history)
        assert features[1] == 0.0  # velocity_count (no window)
        assert features[2] == 0.0  # time_deviation (no history)
        assert features[3] == 0.0  # geo_speed (no location)
        assert features[4] == 0.0  # not blacklisted
        assert features[5] == 0.0  # amount_ratio (no mean)

    def test_blacklisted_flag(self) -> None:
        state = CustomerFraudState(blacklisted=True)
        features = extract_features(state, amount=100.0, hour=14.0)
        assert features[4] == 1.0

    def test_velocity_count_reflects_window(self) -> None:
        state = CustomerFraudState()
        state.velocity_window.add(1000.0)
        state.velocity_window.add(1010.0)
        state.velocity_window.add(1020.0)
        features = extract_features(state, amount=100.0, hour=14.0)
        assert features[1] == 3.0

    def test_amount_ratio_with_history(self) -> None:
        state = CustomerFraudState()
        for v in [100.0, 100.0, 100.0]:
            state.amount_stats.update(v)
        features = extract_features(state, amount=300.0, hour=14.0)
        assert abs(features[5] - 3.0) < 1e-9  # 300/100 = 3.0

    def test_amount_zscore_with_history(self) -> None:
        state = CustomerFraudState()
        for v in [100.0, 100.0, 100.0, 100.0, 100.0]:
            state.amount_stats.update(v)
        # All same value => std_dev = 0 => zscore = 0
        features = extract_features(state, amount=200.0, hour=14.0)
        assert features[0] == 0.0  # std_dev is 0

    def test_amount_zscore_with_variance(self) -> None:
        state = CustomerFraudState()
        for v in [80.0, 90.0, 100.0, 110.0, 120.0]:
            state.amount_stats.update(v)
        features = extract_features(state, amount=200.0, hour=14.0)
        assert features[0] > 0.0  # 200 is above mean of 100

    def test_geo_speed_with_location(self) -> None:
        state = CustomerFraudState(
            last_location=GeoLocation(latitude=-23.55, longitude=-46.63, timestamp_epoch=1000.0)
        )
        features = extract_features(
            state,
            amount=100.0,
            hour=14.0,
            latitude=-3.12,
            longitude=-60.02,
            timestamp_epoch=4600.0,  # 1 hour later
        )
        assert features[3] > 0.0  # Should have speed > 0

    def test_geo_speed_without_location(self) -> None:
        state = CustomerFraudState()
        features = extract_features(
            state,
            amount=100.0,
            hour=14.0,
            latitude=-23.55,
            longitude=-46.63,
            timestamp_epoch=1000.0,
        )
        assert features[3] == 0.0  # No last_location

    def test_all_features_are_float(self) -> None:
        state = CustomerFraudState(blacklisted=True)
        state.velocity_window.add(1000.0)
        state.amount_stats.update(100.0)
        features = extract_features(state, amount=200.0, hour=14.0)
        assert all(isinstance(f, float) for f in features)
