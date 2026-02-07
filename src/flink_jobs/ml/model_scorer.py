"""ML model scorer for anomaly detection.

Loads a pre-trained Isolation Forest model and scores feature vectors.
The decision_function output is normalized to [0, 1] range where:
    - 0.0 = clearly normal
    - 1.0 = highly anomalous

Model is loaded once in Flink's open() and reused for every element.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_MODEL_PATH = Path("models/fraud_model.joblib")


class AnomalyScorer:
    """Score transactions using a pre-trained Isolation Forest model.

    The scorer normalizes sklearn's decision_function (which returns negative
    scores for anomalies) to a [0, 1] range using min-max normalization
    calibrated during training.
    """

    def __init__(
        self,
        model_path: Path | str = DEFAULT_MODEL_PATH,
        score_min: float = -0.5,
        score_max: float = 0.5,
    ) -> None:
        self._model_path = Path(model_path)
        self._model: Any = None
        self._score_min = score_min
        self._score_max = score_max

    def load(self) -> None:
        """Load the model from disk. Call once during Flink open()."""
        try:
            import joblib

            self._model = joblib.load(self._model_path)
            logger.info("ML model loaded from %s", self._model_path)
        except FileNotFoundError:
            logger.warning(
                "Model file not found at %s — ML scoring disabled", self._model_path
            )
            self._model = None
        except ImportError:
            logger.warning("joblib not installed — ML scoring disabled")
            self._model = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def score(self, features: list[float]) -> float:
        """Score a single feature vector.

        Args:
            features: List of numeric features (length must match training).

        Returns:
            Anomaly score in [0, 1] range. Higher = more anomalous.
        """
        if self._model is None:
            return 0.0

        import numpy as np

        feature_array = np.array([features])
        raw_score: float = float(self._model.decision_function(feature_array)[0])

        # Normalize: decision_function returns negative for anomalies
        # More negative = more anomalous, so we invert
        normalized = 1.0 - (raw_score - self._score_min) / (
            self._score_max - self._score_min
        )
        return max(0.0, min(1.0, normalized))
