#!/usr/bin/env python3
"""End-to-end pipeline verification script.

Checks every component of the StreamFlow Analytics pipeline:
  1. Kafka broker connectivity and topic health
  2. PostgreSQL connectivity and schema existence
  3. Bronze/Silver/Gold layer row counts
  4. Flink job status (via K8s API)
  5. Data freshness (last record timestamps)

Usage:
    python scripts/verify_pipeline.py
    python scripts/verify_pipeline.py --env dev --verbose
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any

from psycopg2 import sql

from src.utils.config import load_config
from src.utils.db import get_cursor
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)

CHECK_PASS = "[PASS]"
CHECK_FAIL = "[FAIL]"
CHECK_WARN = "[WARN]"
CHECK_SKIP = "[SKIP]"


class PipelineVerifier:
    """Verify all StreamFlow Analytics pipeline components."""

    def __init__(self, config: dict[str, Any], verbose: bool = False) -> None:
        self.config = config
        self.verbose = verbose
        self.results: list[dict[str, str]] = []

    def _record(self, component: str, status: str, message: str) -> None:
        self.results.append({"component": component, "status": status, "message": message})
        symbol = status
        print(f"  {symbol} {component}: {message}")

    def verify_postgres(self) -> bool:
        """Check PostgreSQL connectivity and schemas."""
        print("\n--- PostgreSQL ---")
        try:
            with get_cursor(self.config) as cur:
                cur.execute("SELECT version()")
                row = cur.fetchone()
                version = row[0] if row else "unknown"
                self._record("pg-connection", CHECK_PASS, f"Connected ({version[:40]}...)")
        except Exception as e:
            self._record("pg-connection", CHECK_FAIL, str(e))
            return False

        # Check schemas exist
        for schema in ("bronze", "silver", "gold"):
            try:
                with get_cursor(self.config) as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name = %s",
                        (schema,),
                    )
                    row = cur.fetchone()
                    exists = row[0] > 0 if row else False
                    if exists:
                        self._record(f"schema-{schema}", CHECK_PASS, "Schema exists")
                    else:
                        self._record(f"schema-{schema}", CHECK_FAIL, "Schema not found")
            except Exception as e:
                self._record(f"schema-{schema}", CHECK_FAIL, str(e))

        return True

    def verify_table_counts(self) -> None:
        """Check row counts in each layer."""
        print("\n--- Data Layers ---")
        tables = [
            ("bronze", "raw_transactions"),
            ("bronze", "raw_fraud_alerts"),
            ("silver", "clean_transactions"),
            ("silver", "customers"),
            ("silver", "stores"),
            ("gold", "fact_transactions"),
            ("gold", "fact_fraud_alerts"),
            ("gold", "dim_customer"),
            ("gold", "dim_store"),
            ("gold", "agg_hourly_sales"),
        ]

        for schema, table in tables:
            try:
                with get_cursor(self.config) as cur:
                    cur.execute(
                        sql.SQL("SELECT COUNT(*) FROM {}.{}").format(
                            sql.Identifier(schema),
                            sql.Identifier(table),
                        )
                    )
                    row = cur.fetchone()
                    count = row[0] if row else 0
                    status = CHECK_PASS if count > 0 else CHECK_WARN
                    self._record(f"{schema}.{table}", status, f"{count:,} rows")
            except Exception as e:
                self._record(f"{schema}.{table}", CHECK_SKIP, str(e)[:60])

    def verify_data_freshness(self) -> None:
        """Check when the latest data was ingested."""
        print("\n--- Data Freshness ---")
        freshness_queries = [
            ("bronze.raw_transactions", "SELECT MAX(ingested_at) FROM bronze.raw_transactions"),
            ("silver.clean_transactions", "SELECT MAX(cleaned_at) FROM silver.clean_transactions"),
        ]

        for name, query in freshness_queries:
            try:
                with get_cursor(self.config) as cur:
                    cur.execute(query)
                    row = cur.fetchone()
                    last_ts = row[0] if row else None
                    if last_ts is None:
                        self._record(name, CHECK_WARN, "No data yet")
                    else:
                        age = datetime.now(UTC) - last_ts
                        minutes = age.total_seconds() / 60
                        status = CHECK_PASS if minutes < 60 else CHECK_WARN
                        self._record(name, status, f"Last record {minutes:.0f} min ago")
            except Exception as e:
                self._record(name, CHECK_SKIP, str(e)[:60])

    def verify_kafka(self) -> None:
        """Check Kafka connectivity via kubectl."""
        print("\n--- Kafka ---")
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "kafka",
                    "-n",
                    "streamflow-kafka",
                    "-o",
                    "jsonpath={.items[0].status.conditions[0].type}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "Ready" in result.stdout:
                self._record("kafka-cluster", CHECK_PASS, "Kafka cluster is Ready")
            else:
                self._record(
                    "kafka-cluster",
                    CHECK_WARN,
                    f"Status: {result.stdout or result.stderr[:60]}",
                )
        except FileNotFoundError:
            self._record("kafka-cluster", CHECK_SKIP, "kubectl not found")
        except subprocess.TimeoutExpired:
            self._record("kafka-cluster", CHECK_SKIP, "kubectl timed out")

        # Check topics
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "kafkatopics",
                    "-n",
                    "streamflow-kafka",
                    "-o",
                    "jsonpath={.items[*].metadata.name}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                topics = result.stdout.split()
                self._record(
                    "kafka-topics", CHECK_PASS, f"{len(topics)} topics: {', '.join(topics)}"
                )
            else:
                self._record("kafka-topics", CHECK_WARN, "No topics found")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self._record("kafka-topics", CHECK_SKIP, "kubectl unavailable")

    def verify_flink(self) -> None:
        """Check Flink job status via kubectl."""
        print("\n--- Flink ---")
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "flinkdeployments",
                    "-n",
                    "streamflow-processing",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                items = data.get("items", [])
                if items:
                    for item in items:
                        name = item["metadata"]["name"]
                        state = item.get("status", {}).get("jobStatus", {}).get("state", "UNKNOWN")
                        status = CHECK_PASS if state == "RUNNING" else CHECK_WARN
                        self._record(f"flink-{name}", status, f"State: {state}")
                else:
                    self._record("flink-jobs", CHECK_WARN, "No FlinkDeployments found")
            else:
                self._record("flink-jobs", CHECK_WARN, result.stderr[:60])
        except FileNotFoundError:
            self._record("flink-jobs", CHECK_SKIP, "kubectl not found")
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            self._record("flink-jobs", CHECK_SKIP, str(e)[:60])

    def verify_airflow(self) -> None:
        """Check Airflow pods are running."""
        print("\n--- Airflow ---")
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pods",
                    "-n",
                    "streamflow-orchestration",
                    "-l",
                    "component in (webserver,scheduler)",
                    "-o",
                    "jsonpath={range .items[*]}{.metadata.name} {.status.phase}\n{end}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split("\n"):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        pod_name, phase = parts[0], parts[1]
                        status = CHECK_PASS if phase == "Running" else CHECK_WARN
                        self._record(f"airflow-{pod_name[:30]}", status, phase)
            else:
                self._record("airflow", CHECK_WARN, "No pods found")
        except (FileNotFoundError, subprocess.TimeoutExpired):
            self._record("airflow", CHECK_SKIP, "kubectl unavailable")

    def run_all(self) -> int:
        """Run all verifications and return exit code."""
        print("=" * 60)
        print("  StreamFlow Analytics — Pipeline Verification")
        print("=" * 60)

        pg_ok = self.verify_postgres()
        if pg_ok:
            self.verify_table_counts()
            self.verify_data_freshness()

        self.verify_kafka()
        self.verify_flink()
        self.verify_airflow()

        # Summary
        print("\n" + "=" * 60)
        passed = sum(1 for r in self.results if r["status"] == CHECK_PASS)
        failed = sum(1 for r in self.results if r["status"] == CHECK_FAIL)
        warned = sum(1 for r in self.results if r["status"] == CHECK_WARN)
        skipped = sum(1 for r in self.results if r["status"] == CHECK_SKIP)
        total = len(self.results)

        print(f"  Total: {total} checks")
        print(
            f"  {CHECK_PASS} {passed}  {CHECK_FAIL} {failed}  {CHECK_WARN} {warned}  {CHECK_SKIP} {skipped}"
        )
        print("=" * 60)

        return 1 if failed > 0 else 0


def main() -> None:
    """Run pipeline verification."""
    parser = argparse.ArgumentParser(description="Verify StreamFlow pipeline")
    parser.add_argument("--config-dir", default="config")
    parser.add_argument("--env", default="dev")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    setup_logging()
    config = load_config(config_dir=args.config_dir, env=args.env)

    verifier = PipelineVerifier(config, verbose=args.verbose)
    exit_code = verifier.run_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
