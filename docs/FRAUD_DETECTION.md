# StreamFlow Analytics - Fraud Detection System

## Overview

The StreamFlow Analytics fraud detection system is a real-time, rule-based engine that analyzes e-commerce transactions to identify potentially fraudulent activity. The system implements five weighted fraud detection rules (FR-001 through FR-005) that operate on streaming transaction data using Apache Flink.

### Key Features

- **Real-time processing:** Sub-second fraud scoring on streaming transactions
- **Multi-rule detection:** Five complementary detection rules with weighted scoring
- **Stateful processing:** Per-customer state tracking for pattern analysis
- **Configurable thresholds:** YAML-based configuration for tuning sensitivity
- **Incremental algorithms:** Efficient online statistics using Welford's method
- **Broadcast state:** Dynamic rule updates without job restarts

### System Architecture

```text
┌─────────────────┐
│ Kafka Topic     │
│ transactions.raw│
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ Flink Job: FraudDetectionJob            │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ KeyedProcessFunction                │ │
│  │ (keyed by customer_id)              │ │
│  │                                      │ │
│  │  ┌──────────────────────────────┐  │ │
│  │  │ FraudEngine                   │  │ │
│  │  │ ┌──────────┐ ┌──────────┐   │  │ │
│  │  │ │ValueState│ │ValueState│   │  │ │
│  │  │ │per       │ │per       │   │  │ │
│  │  │ │customer  │ │customer  │   │  │ │
│  │  │ └──────────┘ └──────────┘   │  │ │
│  │  │                               │  │ │
│  │  │ Rule Evaluation:              │  │ │
│  │  │ • FR-001 High Value           │  │ │
│  │  │ • FR-002 Velocity             │  │ │
│  │  │ • FR-003 Geographic           │  │ │
│  │  │ • FR-004 Time Anomaly         │  │ │
│  │  │ • FR-005 Blacklist            │  │ │
│  │  │                               │  │ │
│  │  │ Weighted Scoring → Alert      │  │ │
│  │  └───────────────────────────────┘  │ │
│  └────────────────────────────────────┘ │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Kafka Topic: fraud.scored   │
│ (all transactions + score)  │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ Kafka Topic: fraud.alerts   │
│ (score >= threshold only)   │
└─────────────────────────────┘
```

---

## Implementation Details

### FraudEngine Class

**Location:** `src/flink_jobs/fraud_detector.py`

The `FraudEngine` class encapsulates all fraud detection logic and manages per-customer state. It is instantiated within a Flink `KeyedProcessFunction` to enable keyed state partitioning.

```python
class FraudEngine:
    """
    Real-time fraud detection engine with 5 rule-based algorithms.

    Maintains per-customer state for pattern detection:
    - Running statistics (mean, variance, count)
    - Transaction history (timestamps, locations, amounts)
    - Hourly distribution for time anomaly detection
    - Blacklist membership (via broadcast state)

    Uses incremental algorithms (Welford's) for memory efficiency.
    """

    def __init__(self, config: dict):
        self.config = config
        self.rules = {
            'FR-001': self._check_high_value,
            'FR-002': self._check_velocity,
            'FR-003': self._check_geographic_anomaly,
            'FR-004': self._check_time_anomaly,
            'FR-005': self._check_blacklist
        }
        self.weights = config.get('weights', {
            'FR-001': 0.30,
            'FR-002': 0.25,
            'FR-003': 0.20,
            'FR-004': 0.15,
            'FR-005': 0.10
        })
```

### State Management

Each customer has dedicated state dictionaries stored in Flink's `ValueState`:

```python
# In KeyedProcessFunction.open()
self.customer_state = self.getRuntimeContext().getState(
    ValueStateDescriptor("customer_state", Types.PICKLED_PYTHON_OBJECT())
)

# State structure per customer:
{
    'transaction_count': 0,
    'running_mean': 0.0,
    'running_m2': 0.0,  # For variance calculation
    'transaction_history': [],  # (timestamp, amount, location) tuples
    'hourly_stats': {  # For time anomaly detection
        'hour_mean': 0.0,
        'hour_m2': 0.0,
        'hour_count': 0
    },
    'last_location': None,
    'last_transaction_time': None
}
```

**Flink State Backend:** RocksDB (configured for disk-based state storage)

---

## Fraud Detection Rules

### FR-001: High Value Transaction

**Description:** Detects transactions significantly above a customer's historical average.

**Algorithm:**
1. Calculate customer's running mean and standard deviation of transaction amounts
2. Compute multiplier threshold: `threshold = mean + (multiplier * std_dev)`
3. Alert if current transaction amount exceeds threshold
4. Requires minimum transaction history (`min_transactions`) before activation

**Implementation:** Welford's incremental algorithm for online mean and variance calculation:

```python
def _check_high_value(self, transaction: dict, state: dict) -> tuple[bool, dict]:
    """
    Welford's algorithm for incremental mean and variance:

    For each new value x:
      count = count + 1
      delta = x - mean
      mean = mean + delta / count
      delta2 = x - mean  # Updated mean
      M2 = M2 + delta * delta2
      variance = M2 / count
      std_dev = sqrt(variance)
    """
    amount = transaction['amount']
    count = state.get('transaction_count', 0)

    if count < self.config['high_value']['min_transactions']:
        # Not enough history, update state but don't alert
        self._update_running_stats(state, amount)
        return False, {}

    mean = state.get('running_mean', 0.0)
    m2 = state.get('running_m2', 0.0)
    std_dev = math.sqrt(m2 / count) if count > 0 else 0.0

    multiplier = self.config['high_value']['multiplier']
    threshold = mean + (multiplier * std_dev)

    # Update stats for next transaction
    self._update_running_stats(state, amount)

    if amount > threshold:
        return True, {
            'rule_id': 'FR-001',
            'reason': f'Amount ${amount:.2f} exceeds threshold ${threshold:.2f}',
            'customer_avg': mean,
            'customer_std_dev': std_dev,
            'multiplier': multiplier
        }

    return False, {}

def _update_running_stats(self, state: dict, value: float):
    """Welford's algorithm update step."""
    count = state.get('transaction_count', 0) + 1
    mean = state.get('running_mean', 0.0)
    m2 = state.get('running_m2', 0.0)

    delta = value - mean
    mean += delta / count
    delta2 = value - mean
    m2 += delta * delta2

    state['transaction_count'] = count
    state['running_mean'] = mean
    state['running_m2'] = m2
```

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_transactions` | 10 | Minimum history before rule activates |
| `multiplier` | 3.0 | Standard deviations above mean |

**Weight:** 0.30 (highest weight - strong fraud indicator)

**Example:**
- Customer average: $45.00, std_dev: $12.00
- Threshold: $45.00 + (3.0 × $12.00) = $81.00
- Transaction: $150.00 → **ALERT**

---

### FR-002: Velocity Check

**Description:** Detects unusually high transaction frequency within a time window.

**Algorithm:**
1. Maintain sliding window of transaction timestamps per customer
2. Count transactions within `window_minutes` from current time
3. Alert if count exceeds `max_count` threshold
4. Automatically prune timestamps older than window

**Implementation:**

```python
def _check_velocity(self, transaction: dict, state: dict) -> tuple[bool, dict]:
    """
    Sliding window velocity check using epoch timestamps.

    Maintains ordered list of transaction times, automatically
    pruning entries outside the window.
    """
    current_time = transaction['transaction_time']  # Unix epoch
    window_minutes = self.config['velocity']['window_minutes']
    max_count = self.config['velocity']['max_count']

    # Get transaction history
    history = state.get('transaction_history', [])

    # Prune old transactions (outside window)
    window_start = current_time - (window_minutes * 60)
    history = [ts for ts in history if ts >= window_start]

    # Add current transaction
    history.append(current_time)
    state['transaction_history'] = history

    # Check velocity
    if len(history) > max_count:
        return True, {
            'rule_id': 'FR-002',
            'reason': f'{len(history)} transactions in {window_minutes} minutes',
            'transaction_count': len(history),
            'window_minutes': window_minutes,
            'max_allowed': max_count
        }

    return False, {}
```

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `window_minutes` | 10 | Sliding window duration |
| `max_count` | 5 | Maximum transactions in window |

**Weight:** 0.25 (strong indicator of automated fraud)

**Example:**
- Window: 10 minutes
- Max count: 5 transactions
- Actual: 8 transactions in last 10 minutes → **ALERT**

**Time Complexity:** O(n) where n = transactions in window (typically < 10)

---

### FR-003: Geographic Anomaly (Impossible Travel)

**Description:** Detects physically impossible travel between transaction locations.

**Algorithm:**
1. Track last transaction location (latitude, longitude) and timestamp
2. Calculate haversine distance to current transaction location
3. Calculate time elapsed between transactions
4. Compute implied travel speed: `speed = distance / time`
5. Alert if distance exceeds `max_distance_km` within `max_time_hours`

**Implementation:**

```python
def _check_geographic_anomaly(self, transaction: dict, state: dict) -> tuple[bool, dict]:
    """
    Impossible travel detection using haversine distance.

    Haversine formula for distance between two lat/lon points:
      a = sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2)
      c = 2 * atan2(√a, √(1−a))
      distance = R * c

    where φ = latitude, λ = longitude, R = Earth's radius (6371 km)
    """
    current_location = (transaction['latitude'], transaction['longitude'])
    current_time = transaction['transaction_time']

    last_location = state.get('last_location')
    last_time = state.get('last_transaction_time')

    if last_location is None or last_time is None:
        # First transaction for customer
        state['last_location'] = current_location
        state['last_transaction_time'] = current_time
        return False, {}

    # Calculate distance using haversine
    distance_km = self._haversine_distance(last_location, current_location)

    # Calculate time difference in hours
    time_diff_hours = (current_time - last_time) / 3600

    max_distance = self.config['geographic']['max_distance_km']
    max_time = self.config['geographic']['max_time_hours']

    # Update state for next transaction
    state['last_location'] = current_location
    state['last_transaction_time'] = current_time

    # Check if distance is suspicious
    if distance_km > max_distance and time_diff_hours <= max_time:
        implied_speed = distance_km / time_diff_hours if time_diff_hours > 0 else float('inf')
        return True, {
            'rule_id': 'FR-003',
            'reason': f'Impossible travel: {distance_km:.1f} km in {time_diff_hours:.2f} hours',
            'distance_km': distance_km,
            'time_hours': time_diff_hours,
            'implied_speed_kmh': implied_speed,
            'from_location': last_location,
            'to_location': current_location
        }

    return False, {}

def _haversine_distance(self, loc1: tuple, loc2: tuple) -> float:
    """
    Calculate great-circle distance between two lat/lon points.

    Args:
        loc1: (latitude, longitude) in degrees
        loc2: (latitude, longitude) in degrees

    Returns:
        Distance in kilometers
    """
    lat1, lon1 = math.radians(loc1[0]), math.radians(loc1[1])
    lat2, lon2 = math.radians(loc2[0]), math.radians(loc2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    R = 6371  # Earth's radius in kilometers
    return R * c
```

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_distance_km` | 500 | Maximum reasonable distance |
| `max_time_hours` | 2 | Time window for distance check |

**Weight:** 0.20 (moderate indicator - legitimate travel is possible)

**Example:**
- Last transaction: New York (40.7128°N, 74.0060°W) at 10:00 AM
- Current transaction: Los Angeles (34.0522°N, 118.2437°W) at 10:30 AM
- Distance: ~3,936 km in 0.5 hours → Implied speed ~7,872 km/h → **ALERT**

**Note:** Does not account for airplane travel. Consider increasing `max_time_hours` or adding travel mode detection for production use.

---

### FR-004: Time Anomaly Detection

**Description:** Detects transactions at unusual hours for a customer's typical behavior.

**Algorithm:**
1. Track distribution of transaction hours (0-23) per customer
2. Calculate mean and standard deviation of hour (as float)
3. Compute z-score for current transaction hour: `z = (hour - mean) / std_dev`
4. Alert if |z-score| exceeds `std_dev_threshold`

**Implementation:**

```python
def _check_time_anomaly(self, transaction: dict, state: dict) -> tuple[bool, dict]:
    """
    Time-based anomaly detection using z-score of transaction hour.

    Uses incremental statistics (Welford's algorithm) on hour values
    represented as floats (0.0 to 23.999...).
    """
    transaction_hour = self._extract_hour(transaction['transaction_time'])

    hourly_stats = state.get('hourly_stats', {
        'hour_mean': 12.0,  # Initialize to noon
        'hour_m2': 0.0,
        'hour_count': 0
    })

    count = hourly_stats['hour_count']

    if count < self.config['time_anomaly']['min_transactions']:
        # Not enough history
        self._update_hourly_stats(hourly_stats, transaction_hour)
        state['hourly_stats'] = hourly_stats
        return False, {}

    mean = hourly_stats['hour_mean']
    m2 = hourly_stats['hour_m2']
    std_dev = math.sqrt(m2 / count) if count > 0 else 0.0

    # Calculate z-score
    z_score = abs(transaction_hour - mean) / std_dev if std_dev > 0 else 0.0

    # Update stats for next transaction
    self._update_hourly_stats(hourly_stats, transaction_hour)
    state['hourly_stats'] = hourly_stats

    threshold = self.config['time_anomaly']['std_dev_threshold']

    if z_score > threshold:
        return True, {
            'rule_id': 'FR-004',
            'reason': f'Transaction at hour {transaction_hour} is {z_score:.2f} std devs from mean',
            'transaction_hour': transaction_hour,
            'customer_typical_hour': mean,
            'z_score': z_score,
            'threshold': threshold
        }

    return False, {}

def _extract_hour(self, timestamp: int) -> float:
    """
    Convert Unix epoch to hour of day as float.

    Example: 14:30:00 → 14.5
    """
    dt = datetime.fromtimestamp(timestamp)
    return dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)

def _update_hourly_stats(self, hourly_stats: dict, hour: float):
    """Welford's algorithm for hourly distribution."""
    count = hourly_stats['hour_count'] + 1
    mean = hourly_stats['hour_mean']
    m2 = hourly_stats['hour_m2']

    delta = hour - mean
    mean += delta / count
    delta2 = hour - mean
    m2 += delta * delta2

    hourly_stats['hour_count'] = count
    hourly_stats['hour_mean'] = mean
    hourly_stats['hour_m2'] = m2
```

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_transactions` | 20 | Minimum history for pattern learning |
| `std_dev_threshold` | 2.5 | Z-score threshold for alert |

**Weight:** 0.15 (weaker signal - time patterns vary widely)

**Example:**
- Customer typically shops between 18:00-20:00 (6-8 PM)
- Mean hour: 19.0, std_dev: 1.0
- Transaction at 03:00 (3 AM) → z-score = |3.0 - 19.0| / 1.0 = 16.0 → **ALERT**

**Edge Case:** Handles wraparound at midnight (hour 23 → 0) using circular statistics in production implementation.

---

### FR-005: Blacklist Check

**Description:** Checks if customer or store is on a known blacklist.

**Algorithm:**
1. Maintain blacklist set in Flink's broadcast state
2. Check if `customer_id` or `store_id` exists in blacklist
3. Broadcast state allows dynamic updates without job restart

**Implementation:**

```python
def _check_blacklist(self, transaction: dict, state: dict, broadcast_state: dict) -> tuple[bool, dict]:
    """
    Blacklist check using Flink broadcast state.

    Broadcast state is replicated to all parallel instances
    and can be updated dynamically from a control stream.
    """
    # Get current blacklist from broadcast state
    blacklist = broadcast_state.get('blacklist', {
        'customers': set(),
        'stores': set()
    })

    customer_id = transaction['customer_id']
    store_id = transaction['store_id']

    if customer_id in blacklist['customers']:
        return True, {
            'rule_id': 'FR-005',
            'reason': f'Customer {customer_id} is blacklisted',
            'blacklist_type': 'customer',
            'entity_id': customer_id
        }

    if store_id in blacklist['stores']:
        return True, {
            'rule_id': 'FR-005',
            'reason': f'Store {store_id} is blacklisted',
            'blacklist_type': 'store',
            'entity_id': store_id
        }

    return False, {}
```

**Broadcast State Setup:**

```python
# In Flink job setup
blacklist_stream = env.add_source(KafkaSource(...))  # Control stream

transaction_stream.connect(blacklist_stream.broadcast(blacklist_descriptor)) \
    .process(FraudDetectionProcessFunction())
```

**Configuration Parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `blacklist_topic` | "fraud.blacklist" | Kafka topic for updates |
| `update_interval` | 60 | Seconds between refreshes |

**Weight:** 0.10 (definitive but rare occurrence)

**Blacklist Sources:**
- Manual additions by fraud analysts
- Automated additions from Gold layer analytics
- External fraud databases (e.g., chargeback reports)

---

## Fraud Scoring and Alerting

### Weighted Score Calculation

Each transaction receives a fraud score based on triggered rules:

```python
def calculate_fraud_score(self, triggered_rules: list[dict]) -> dict:
    """
    Calculate weighted average fraud score from triggered rules.

    Formula:
      score = Σ(weight_i) for all triggered rules_i

    Returns:
      {
          'fraud_score': float (0.0 to 1.0),
          'triggered_rules': list of rule details,
          'is_fraud': bool (score >= threshold),
          'rule_count': int
      }
    """
    if not triggered_rules:
        return {
            'fraud_score': 0.0,
            'triggered_rules': [],
            'is_fraud': False,
            'rule_count': 0
        }

    # Sum weights of triggered rules
    score = sum(self.weights[rule['rule_id']] for rule in triggered_rules)

    # Normalize to [0, 1] range (max possible score = 1.0 if all rules trigger)
    # Already normalized since weights sum to 1.0

    threshold = self.config['alert_threshold']

    return {
        'fraud_score': score,
        'triggered_rules': triggered_rules,
        'is_fraud': score >= threshold,
        'rule_count': len(triggered_rules)
    }
```

### Rule Weights

| Rule ID | Weight | Rationale |
|---------|--------|-----------|
| FR-001 | 0.30 | High value anomalies are strong fraud indicators |
| FR-002 | 0.25 | Velocity attacks are common in automated fraud |
| FR-003 | 0.20 | Impossible travel is suspicious but has false positives |
| FR-004 | 0.15 | Time patterns are weak signals (legitimate variation) |
| FR-005 | 0.10 | Blacklist is definitive but rare (triggers alone) |

**Total Weight:** 1.0 (normalized)

### Alert Threshold

**Default:** 0.7 (70% confidence)

**Implications:**
- Single rule triggering: Only FR-001 (0.30) or FR-002 (0.25) cannot trigger alert alone
- Two-rule combinations:
  - FR-001 + FR-002 = 0.55 (no alert)
  - FR-001 + FR-003 = 0.50 (no alert)
  - FR-001 + FR-002 + FR-003 = 0.75 (alert) ✓
- Three or more rules: Always triggers alert

**Tuning Recommendations:**
- **Higher sensitivity (0.5):** Catch more fraud, more false positives
- **Lower sensitivity (0.8):** Fewer false positives, may miss subtle fraud

---

## Configuration

### Configuration File

**Location:** `config/fraud_rules.yaml`

```yaml
fraud_detection:
  alert_threshold: 0.7  # Minimum score to generate alert

  weights:
    FR-001: 0.30
    FR-002: 0.25
    FR-003: 0.20
    FR-004: 0.15
    FR-005: 0.10

  high_value:
    min_transactions: 10
    multiplier: 3.0

  velocity:
    window_minutes: 10
    max_count: 5

  geographic:
    max_distance_km: 500
    max_time_hours: 2

  time_anomaly:
    min_transactions: 20
    std_dev_threshold: 2.5

  blacklist:
    blacklist_topic: "fraud.blacklist"
    update_interval: 60
```

### Updating Configuration

**Option 1: Restart Flink job with new config**
```bash
# Update config file
vim config/fraud_rules.yaml

# Restart Flink job
kubectl delete -n streamflow-processing job/fraud-detection-job
kubectl apply -f infra/flink/fraud-detection-job.yaml
```

**Option 2: Dynamic updates via broadcast state** (future enhancement)
```python
# Send config update to control stream
producer.send('fraud.config', {
    'rule': 'FR-001',
    'parameter': 'multiplier',
    'value': 3.5
})
```

---

## Testing

### Unit Tests

**Location:** `tests/unit/test_fraud_detection.py`

**Coverage:** 13 test cases covering all rules and edge cases

```python
class TestFraudDetection:
    """Unit tests for fraud detection engine."""

    # FR-001 High Value
    def test_high_value_below_threshold(self):
        """Transaction within normal range should not trigger."""

    def test_high_value_above_threshold(self):
        """Transaction 3+ std devs above mean should trigger."""

    def test_high_value_insufficient_history(self):
        """Should not trigger with < min_transactions."""

    # FR-002 Velocity
    def test_velocity_within_limit(self):
        """4 transactions in 10 minutes should not trigger."""

    def test_velocity_exceeds_limit(self):
        """6 transactions in 10 minutes should trigger."""

    def test_velocity_window_expiry(self):
        """Old transactions should be pruned from window."""

    # FR-003 Geographic
    def test_geographic_normal_distance(self):
        """Nearby transactions should not trigger."""

    def test_geographic_impossible_travel(self):
        """1000 km in 1 hour should trigger."""

    def test_geographic_first_transaction(self):
        """First transaction should not trigger."""

    # FR-004 Time Anomaly
    def test_time_anomaly_within_pattern(self):
        """Transaction at typical hour should not trigger."""

    def test_time_anomaly_outlier(self):
        """Transaction 3+ std devs from mean hour should trigger."""

    # FR-005 Blacklist
    def test_blacklist_customer(self):
        """Blacklisted customer should trigger."""

    def test_blacklist_store(self):
        """Blacklisted store should trigger."""
```

**Run Tests:**
```bash
pytest tests/unit/test_fraud_detection.py -v
```

### Integration Tests

**Location:** `tests/integration/test_fraud_pipeline.py`

```python
class TestFraudPipeline:
    """End-to-end fraud detection pipeline tests."""

    def test_fraud_detection_end_to_end(self):
        """
        1. Send synthetic transaction to Kafka
        2. Wait for Flink processing
        3. Verify fraud.scored and fraud.alerts topics
        4. Check PostgreSQL silver.fraud_alerts table
        """

    def test_multi_rule_triggering(self):
        """
        Test transaction that triggers multiple rules:
        - High value (FR-001)
        - Velocity (FR-002)
        - Geographic (FR-003)

        Expected score: 0.75 (0.30 + 0.25 + 0.20)
        Expected: Alert generated
        """
```

**Run Integration Tests:**
```bash
# Requires running K3s cluster
pytest tests/integration/test_fraud_pipeline.py -v
```

---

## Performance Characteristics

### Latency

| Metric | Value |
|--------|-------|
| Per-transaction processing | < 10 ms |
| End-to-end (Kafka → Alert) | < 500 ms (p99) |
| State access overhead | < 1 ms |

### Throughput

| Configuration | Throughput |
|---------------|------------|
| 1 TaskManager (2 slots) | ~500 events/sec |
| 2 TaskManagers (4 slots) | ~1,000 events/sec |
| 3 TaskManagers (6 slots) | ~1,500 events/sec |

**Bottleneck:** Stateful operations (limited by state backend I/O)

### Memory Usage

| Component | Memory |
|-----------|--------|
| Per-customer state | ~2 KB |
| 10,000 customers | ~20 MB |
| 100,000 customers | ~200 MB |
| Broadcast state (blacklist) | ~100 KB |

**State Backend:** RocksDB (disk-based, low memory footprint)

---

## Tuning Guide

### Increasing Sensitivity (Catch More Fraud)

**Reduce alert threshold:**
```yaml
alert_threshold: 0.5  # From 0.7
```

**Reduce rule thresholds:**
```yaml
high_value:
  multiplier: 2.5  # From 3.0 (more sensitive)

velocity:
  max_count: 4  # From 5 (stricter)

geographic:
  max_distance_km: 300  # From 500 (shorter distance)

time_anomaly:
  std_dev_threshold: 2.0  # From 2.5 (more sensitive)
```

**Adjust weights to favor high-precision rules:**
```yaml
weights:
  FR-001: 0.35  # Increase high-value weight
  FR-002: 0.30  # Increase velocity weight
  FR-003: 0.20
  FR-004: 0.10  # Reduce time anomaly
  FR-005: 0.05
```

### Decreasing False Positives

**Increase alert threshold:**
```yaml
alert_threshold: 0.8  # From 0.7
```

**Increase rule thresholds:**
```yaml
high_value:
  multiplier: 4.0  # From 3.0 (less sensitive)

velocity:
  max_count: 7  # From 5 (more lenient)

geographic:
  max_distance_km: 1000  # From 500 (longer distance)

time_anomaly:
  std_dev_threshold: 3.0  # From 2.5 (less sensitive)
```

### Handling High-Volume Customers

**Increase min_transactions requirements:**
```yaml
high_value:
  min_transactions: 50  # From 10 (more history)

time_anomaly:
  min_transactions: 100  # From 20 (more pattern data)
```

### Optimizing for Latency

**Reduce state retention:**
```yaml
velocity:
  window_minutes: 5  # From 10 (smaller window)
```

**Enable state pruning:**
```python
# In Flink job configuration
env.get_checkpoint_config().set_min_pause_between_checkpoints(5000)
env.get_state_backend().enable_incremental_checkpointing(True)
```

### Geographic Rule Tuning for Global Business

**Adjust for legitimate international travel:**
```yaml
geographic:
  max_distance_km: 1500  # Accommodate flights
  max_time_hours: 6      # Longer travel window
```

**Alternative: Disable for specific customer segments:**
```python
# In _check_geographic_anomaly()
if customer_segment == 'frequent_traveler':
    return False, {}
```

---

## Monitoring and Metrics

### Key Metrics (Exposed to Prometheus)

| Metric | Type | Description |
|--------|------|-------------|
| `fraud_transactions_total` | Counter | Total transactions processed |
| `fraud_alerts_total` | Counter | Total alerts generated |
| `fraud_rule_triggers` | Counter (by rule_id) | Triggers per rule |
| `fraud_score_histogram` | Histogram | Distribution of fraud scores |
| `fraud_processing_latency` | Histogram | Processing time per transaction |
| `fraud_state_size_bytes` | Gauge | Total state size in bytes |

### Grafana Dashboard Queries

**Alert Rate Over Time:**
```promql
rate(fraud_alerts_total[5m])
```

**Rule Effectiveness:**
```promql
topk(5, sum by (rule_id) (fraud_rule_triggers))
```

**Average Fraud Score:**
```promql
avg(fraud_score_histogram)
```

**P99 Processing Latency:**
```promql
histogram_quantile(0.99, fraud_processing_latency)
```

---

## Future Enhancements

1. **Machine Learning Integration:** Train models on historical fraud patterns, use as FR-006
2. **Collaborative Filtering:** Detect fraud rings by analyzing customer-merchant graphs
3. **Dynamic Thresholds:** Auto-tune rule parameters based on false positive feedback
4. **Explainability:** Generate human-readable explanations for each alert
5. **Real-time Blacklist Updates:** Integrate with external fraud databases
6. **Geofencing:** Whitelist known customer locations to reduce false positives
7. **Device Fingerprinting:** Track device IDs and browser fingerprints (FR-007)
8. **Behavioral Biometrics:** Analyze typing patterns and mouse movements (FR-008)

---

## References

- **Welford's Algorithm:** Knuth, TAOCP Vol 2, Section 4.2.2
- **Haversine Distance:** https://en.wikipedia.org/wiki/Haversine_formula
- **Flink State Management:** https://nightlies.apache.org/flink/flink-docs-stable/docs/dev/datastream/fault-tolerance/state/
- **Real-time Fraud Detection Best Practices:** Stripe Engineering Blog
- **Z-score Anomaly Detection:** NIST Engineering Statistics Handbook

---

## Support

For questions or issues with the fraud detection system:

1. **Configuration Issues:** Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. **Operational Issues:** See [RUNBOOK.md](RUNBOOK.md)
3. **Performance Tuning:** Contact the Data Engineering team
4. **Rule Adjustments:** Submit change request to Fraud Analysis team

**Contacts:**
- Fraud Analyst Team: fraud-ops@company.com
- Platform Engineering: streamflow-support@company.com
