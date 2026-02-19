# ADR 006: PyFlink Docker Image Without Custom JAR Build

## Status

Accepted

## Date

2026-02-18

## Context

The Flink K8s manifests referenced `streamflow-jobs.jar` which didn't exist.
The project uses PyFlink (Python) for all Flink jobs. We needed a way to run
Python Flink jobs on the Flink Kubernetes Operator.

## Decision

Use the **built-in PythonDriver JAR** (`flink-python_2.12-1.20.0.jar`) that ships
with the `flink:1.20-java17` base image. Create a custom Docker image that adds:

- Python 3.12 + PyFlink 1.20.0
- scikit-learn (for ML fraud detection)
- Source code copied to `/opt/flink/usrlib/src/`

FlinkDeployment manifests updated:

```yaml
job:
  jarURI: local:///opt/flink/opt/flink-python_2.12-1.20.0.jar
  entryClass: org.apache.flink.client.python.PythonDriver
  args:
    - "-pyclientexec"
    - "/usr/bin/python3"
    - "-py"
    - "/opt/flink/usrlib/src/flink_jobs/fraud_detector.py"
```

## Consequences

### Positive

- **Zero Java toolchain**: No Maven, Gradle, or JAR build step
- **Simple Dockerfile**: Standard `flink:1.20-java17` base + `pip install`
- **Standard pattern**: Follows official Flink K8s Operator Python examples
- **Fast builds**: Docker build takes ~2min vs ~10min for Maven fat JAR

### Negative

- Flink image is larger (~1.5GB with Python + PyFlink + scikit-learn)
- Python execution slightly slower than native Java (acceptable for our throughput)

## Alternatives Considered

1. **Maven fat JAR** with PyFlink — Adds Java build complexity, 10+ min build
2. **Replace Flink with pure Python Kafka consumer** — Loses checkpointing,
   state management, exactly-once semantics
3. **GraalVM native image** — Experimental, not supported by Flink Operator
