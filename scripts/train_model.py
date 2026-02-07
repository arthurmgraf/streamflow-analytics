"""Train Isolation Forest model for fraud anomaly detection.

Uses the existing TransactionGenerator and FraudInjector to create
synthetic training data, extracts features, and saves model to disk.

Usage:
    python scripts/train_model.py [--output models/fraud_model.joblib] [--samples 10000]
"""

from __future__ import annotations

import argparse
import datetime
import logging
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

from src.flink_jobs.common.state import CustomerFraudState
from src.flink_jobs.fraud_detector import FraudRuleEvaluator
from src.flink_jobs.ml.feature_engineering import extract_features
from src.generators.customer_generator import generate_customers
from src.generators.fraud_patterns import FraudInjector
from src.generators.store_generator import generate_stores
from src.generators.transaction_generator import TransactionGenerator

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def generate_training_data(
    n_samples: int = 10000,
    fraud_rate: float = 0.02,
    seed: int = 42,
) -> tuple[np.ndarray, list[bool]]:
    """Generate feature vectors from synthetic transactions.

    Returns:
        Tuple of (feature_matrix [n_samples, 6], is_fraud labels).
    """
    customers = generate_customers(100, seed=seed)
    stores = generate_stores(20, seed=seed)
    generator = TransactionGenerator(customers=customers, stores=stores, seed=seed)
    injector = FraudInjector(
        customers=customers, stores=stores, fraud_rate=fraud_rate, seed=seed,
    )
    evaluator = FraudRuleEvaluator()

    states: dict[str, CustomerFraudState] = {}
    features_list: list[list[float]] = []
    labels: list[bool] = []

    base_time = time.time() - n_samples * 60

    for i in range(n_samples):
        txn = generator.generate()
        is_fraud = injector.should_inject()
        if is_fraud:
            txn = injector.inject(txn)

        customer_id = txn.customer_id
        if customer_id not in states:
            states[customer_id] = CustomerFraudState()
        state = states[customer_id]

        amount = float(txn.amount)
        timestamp_epoch = base_time + i * 60

        dt = datetime.datetime.fromtimestamp(timestamp_epoch)
        hour = dt.hour + dt.minute / 60

        feature_vec = extract_features(
            state=state,
            amount=amount,
            hour=hour,
            latitude=txn.latitude,
            longitude=txn.longitude,
            timestamp_epoch=timestamp_epoch,
        )
        features_list.append(feature_vec)
        labels.append(is_fraud)

        evaluator.evaluate(
            state=state,
            amount=amount,
            timestamp_epoch=timestamp_epoch,
            latitude=txn.latitude,
            longitude=txn.longitude,
            store_id=txn.store_id,
        )

    return np.array(features_list), labels


def train_and_save(
    output_path: Path,
    n_samples: int = 10000,
    contamination: float = 0.02,
    n_estimators: int = 100,
    seed: int = 42,
) -> None:
    """Train Isolation Forest and save to disk."""
    logger.info("Generating %d training samples...", n_samples)
    features, labels = generate_training_data(n_samples=n_samples, seed=seed)

    fraud_count = sum(labels)
    logger.info(
        "Training data: %d total, %d fraud (%.1f%%)",
        n_samples,
        fraud_count,
        100 * fraud_count / n_samples,
    )

    logger.info(
        "Training IsolationForest (n_estimators=%d, contamination=%.3f)...",
        n_estimators,
        contamination,
    )
    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=seed,
        n_jobs=-1,
    )
    model.fit(features)

    scores = model.decision_function(features)
    logger.info(
        "Score range: [%.4f, %.4f], mean=%.4f",
        float(np.min(scores)),
        float(np.max(scores)),
        float(np.mean(scores)),
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
    logger.info("Model saved to %s", output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train fraud detection ML model")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("models/fraud_model.joblib"),
        help="Output model path",
    )
    parser.add_argument("--samples", type=int, default=10000, help="Training samples")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    train_and_save(output_path=args.output, n_samples=args.samples, seed=args.seed)


if __name__ == "__main__":
    main()
