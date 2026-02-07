"""Feature engineering for ML-based anomaly detection.

Extracts a numeric feature vector from CustomerFraudState + current transaction.
Pure Python — no Flink or sklearn dependencies. Testable in isolation.

Feature vector (6 dimensions):
    0. amount_zscore    — how many std devs the amount deviates from customer mean
    1. velocity_count   — number of transactions in the current window
    2. time_deviation   — z-score of transaction hour vs customer's typical hours
    3. geo_speed_kmh    — implied travel speed from last known location (km/h)
    4. is_blacklisted   — 1.0 if customer/store is blacklisted, else 0.0
    5. amount_ratio     — current amount / customer average (0 if no history)
"""

from __future__ import annotations

from src.flink_jobs.common.state import CustomerFraudState, GeoLocation, haversine_km

FEATURE_NAMES = [
    "amount_zscore",
    "velocity_count",
    "time_deviation",
    "geo_speed_kmh",
    "is_blacklisted",
    "amount_ratio",
]

NUM_FEATURES = len(FEATURE_NAMES)


def extract_features(
    state: CustomerFraudState,
    amount: float,
    hour: float,
    latitude: float | None = None,
    longitude: float | None = None,
    timestamp_epoch: float = 0.0,
) -> list[float]:
    """Extract feature vector from customer state and current transaction.

    Args:
        state: Current per-customer fraud state.
        amount: Transaction amount.
        hour: Transaction hour as float (e.g., 14.5 for 14:30).
        latitude: Transaction latitude (optional).
        longitude: Transaction longitude (optional).
        timestamp_epoch: Transaction timestamp in epoch seconds.

    Returns:
        List of 6 floats representing the feature vector.
    """
    amount_zscore = _compute_zscore(amount, state.amount_stats.mean, state.amount_stats.std_dev)
    velocity_count = float(state.velocity_window.count)
    time_deviation = _compute_zscore(hour, state.hour_stats.mean, state.hour_stats.std_dev)
    geo_speed = _compute_geo_speed(
        state.last_location, latitude, longitude, timestamp_epoch
    )
    is_blacklisted = 1.0 if state.blacklisted else 0.0
    amount_ratio = (
        amount / state.amount_stats.mean if state.amount_stats.mean > 0 else 0.0
    )

    return [
        amount_zscore,
        velocity_count,
        time_deviation,
        geo_speed,
        is_blacklisted,
        amount_ratio,
    ]


def _compute_zscore(value: float, mean: float, std_dev: float) -> float:
    if std_dev <= 0 or mean == 0:
        return 0.0
    return (value - mean) / std_dev


def _compute_geo_speed(
    last_location: GeoLocation | None,
    latitude: float | None,
    longitude: float | None,
    timestamp_epoch: float,
) -> float:
    if last_location is None or latitude is None or longitude is None:
        return 0.0
    time_hours = (timestamp_epoch - last_location.timestamp_epoch) / 3600
    if time_hours <= 0:
        return 0.0
    distance_km = haversine_km(
        last_location.latitude, last_location.longitude, latitude, longitude
    )
    return distance_km / time_hours
