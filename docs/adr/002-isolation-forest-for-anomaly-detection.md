# ADR-002: Isolation Forest for ML-Based Anomaly Detection

## Status
Accepted

## Date
2026-01-20

## Context
The rule-based fraud detection engine (5 rules: high value, velocity, geographic, time anomaly, blacklist) catches known fraud patterns but misses novel attack vectors. We need an ML component for anomaly detection.

**Options considered:**
1. **Isolation Forest** — Unsupervised, fast inference, works with small datasets, interpretable
2. **XGBoost** — Supervised, requires labeled fraud data, higher accuracy on known patterns
3. **Autoencoder** — Deep learning, captures complex patterns, requires GPU for training
4. **One-Class SVM** — Classical anomaly detection, poor scaling with high dimensionality

## Decision
We chose **Isolation Forest** because:

1. **Unsupervised**: No labeled fraud data required — critical since we're bootstrapping
2. **Fast inference**: O(log n) per prediction, suitable for real-time scoring in Flink
3. **Low resource**: CPU-only, no GPU needed; model file is <5MB
4. **Interpretable**: `decision_function` scores map to anomaly severity
5. **Proven**: Widely used in financial fraud detection (PayPal, Stripe research papers)

**Hybrid scoring approach:**
```
final_score = alpha * ml_score + (1 - alpha) * rules_score
```
Where `alpha = 0.3` (configurable) — rules remain primary, ML augments.

## Consequences
- New dependency: `scikit-learn >= 1.4.0`, `joblib >= 1.3.0`
- Offline training script generates model from synthetic data
- Model versioned in `models/` directory with timestamp
- Feature vector: 6 dimensions (amount_zscore, velocity_count, time_deviation, geo_speed_kmh, is_blacklisted, amount_ratio)
- Model retraining triggered manually or via scheduled DAG
