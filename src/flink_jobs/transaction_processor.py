"""Transaction processor: Kafka → validate → Bronze.

Reads raw transaction events from Kafka, validates with Pydantic,
and sinks valid events to PostgreSQL bronze.raw_transactions.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pyflink.common import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.jdbc import (
    JdbcConnectionOptions,
    JdbcExecutionOptions,
    JdbcSink,
)
from pyflink.datastream.connectors.kafka import (
    KafkaOffsetsInitializer,
    KafkaSource,
)

from src.flink_jobs.common.schemas import BRONZE_RAW_TRANSACTIONS_INSERT
from src.models.transaction import Transaction

logger = logging.getLogger(__name__)


def _parse_and_validate(raw: str) -> dict[str, Any] | None:
    """Parse JSON and validate against Transaction model.

    Returns a dict with Kafka metadata + raw payload for Bronze insertion,
    or None if the event is malformed.
    """
    try:
        data: dict[str, Any] = json.loads(raw)
        txn = Transaction(**data)
        return {
            "event_timestamp": txn.timestamp.isoformat(),
            "raw_payload": json.dumps(txn.to_json_dict(), default=str),
            "schema_version": 1,
        }
    except (json.JSONDecodeError, ValueError):
        logger.warning("Skipping malformed event: %s", raw[:200])
        return None


def build_pipeline(env: StreamExecutionEnvironment, config: dict[str, Any]) -> None:
    """Build the transaction processing pipeline.

    Args:
        env: Flink streaming execution environment.
        config: Application configuration dict.
    """
    kafka_cfg = config["kafka"]
    pg_cfg = config["postgres"]

    # Kafka Source
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(kafka_cfg["bootstrap_servers"])
        .set_topics(kafka_cfg["topics"]["transactions"])
        .set_group_id("flink-transaction-processor")
        .set_starting_offsets(KafkaOffsetsInitializer.latest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    ds = env.from_source(
        kafka_source,
        WatermarkStrategy.for_monotonous_timestamps(),
        "kafka-transactions",
    )

    # Parse + validate
    validated = ds.map(_parse_and_validate).filter(lambda x: x is not None)

    # JDBC Sink to Bronze
    jdbc_url = f"jdbc:postgresql://{pg_cfg['host']}:{pg_cfg.get('port', 5432)}/{pg_cfg['database']}"

    jdbc_sink = JdbcSink.sink(
        BRONZE_RAW_TRANSACTIONS_INSERT,
        type_info=None,  # Type info resolved at runtime
        jdbc_connection_options=(
            JdbcConnectionOptions.JdbcConnectionOptionsBuilder()
            .with_url(jdbc_url)
            .with_driver_name("org.postgresql.Driver")
            .with_user_name(pg_cfg["user"])
            .with_password(pg_cfg.get("password", ""))
            .build()
        ),
        jdbc_execution_options=(
            JdbcExecutionOptions.builder()
            .with_batch_interval_ms(1000)
            .with_batch_size(100)
            .with_max_retries(3)
            .build()
        ),
    )

    validated.add_sink(jdbc_sink)


def main(config: dict[str, Any]) -> None:
    """Entry point for the transaction processor job."""
    env = StreamExecutionEnvironment.get_execution_environment()

    flink_cfg = config.get("flink", {})
    env.enable_checkpointing(flink_cfg.get("checkpoint_interval_ms", 60000))
    env.set_parallelism(flink_cfg.get("parallelism", 2))

    build_pipeline(env, config)
    env.execute("streamflow-transaction-processor")
