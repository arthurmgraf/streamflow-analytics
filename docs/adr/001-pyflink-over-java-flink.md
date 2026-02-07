# ADR-001: PyFlink over Java Flink for Stream Processing

## Status
Accepted

## Date
2026-01-15

## Context
StreamFlow Analytics requires a stream processing engine for real-time fraud detection. Apache Flink is the industry standard for stateful stream processing, but it can be used via Java/Scala or Python (PyFlink).

**Options considered:**
1. **Java Flink** - Native performance, full API surface, largest community
2. **PyFlink** - Python ecosystem integration, easier ML model loading, team expertise
3. **Kafka Streams** - Simpler deployment, but limited windowing and state management

## Decision
We chose **PyFlink** for the following reasons:

1. **ML Integration**: Fraud detection requires loading scikit-learn models (Isolation Forest). PyFlink allows direct joblib.load() in open() without JNI bridges
2. **Team expertise**: Data engineering team is Python-first; Java would slow development by 2-3x
3. **Feature parity**: PyFlink supports KeyedProcessFunction, ValueState, ListState, checkpointing, and side outputs - all required for our use case
4. **Shared codebase**: Feature engineering and model training scripts are Python; PyFlink avoids language boundary

**Trade-offs accepted:**
- ~15-20%% performance overhead vs Java Flink (acceptable for our 10K TPS target)
- Smaller community for Python-specific Flink issues
- Some advanced features (e.g., custom timers) have less documentation

## Consequences
- All Flink jobs written in Python using KeyedProcessFunction
- State serialization uses msgpack for to_bytes()/from_bytes()
- ML models loaded via joblib in the open() lifecycle method
- RocksDB state backend for production (in-memory for tests)
