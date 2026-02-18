"""Fraud detection pipeline: Kafka → FraudDetectorFunction → Sinks.

Builds the complete streaming pipeline for real-time fraud detection:
1. KafkaSource reads validated transactions
2. key_by(customer_id) partitions the stream
3. FraudDetectorFunction evaluates 5 fraud rules with fault-tolerant state
4. Main output: enriched transactions → PostgreSQL bronze
5. Side output: fraud alerts → Kafka fraud-alerts topic + PostgreSQL
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
    KafkaRecordSerializationSchema,
    KafkaSink,
    KafkaSource,
)

from src.flink_jobs.common.schemas import BRONZE_RAW_FRAUD_ALERTS_INSERT
from src.flink_jobs.fraud_detector_function import FRAUD_ALERT_TAG, FraudDetectorFunction

logger = logging.getLogger(__name__)


def _extract_customer_id(value: str) -> str:
    try:
        data: dict[str, Any] = json.loads(value)
        return str(data.get("customer_id", "unknown"))
    except json.JSONDecodeError:
        return "unknown"


def build_fraud_detection_pipeline(
    env: StreamExecutionEnvironment,
    config: dict[str, Any],
) -> None:
    """Build the fraud detection streaming pipeline.

    Args:
        env: Flink streaming execution environment.
        config: Application configuration dict with kafka, postgres, flink sections.
    """
    kafka_cfg = config["kafka"]
    pg_cfg = config["postgres"]
    fraud_cfg = config.get("fraud_rules")

    # Source: validated transactions from Kafka
    kafka_source = (
        KafkaSource.builder()
        .set_bootstrap_servers(kafka_cfg["bootstrap_servers"])
        .set_topics(kafka_cfg["topics"]["transactions"])
        .set_group_id("flink-fraud-detector")
        .set_starting_offsets(KafkaOffsetsInitializer.latest())
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    transactions = env.from_source(
        kafka_source,
        WatermarkStrategy.for_monotonous_timestamps(),
        "kafka-transactions",
    )

    # Key by customer_id → enables per-customer state in FraudDetectorFunction
    keyed_stream = transactions.key_by(_extract_customer_id)

    # Process: FraudDetectorFunction with fault-tolerant state
    fraud_detector = FraudDetectorFunction(rules_config=fraud_cfg)
    processed = keyed_stream.process(fraud_detector, output_tag=FRAUD_ALERT_TAG)

    # Side output: fraud alerts → Kafka
    fraud_alerts = processed.get_side_output(FRAUD_ALERT_TAG)

    kafka_alert_sink = (
        KafkaSink.builder()
        .set_bootstrap_servers(kafka_cfg["bootstrap_servers"])
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(kafka_cfg["topics"].get("fraud_alerts", "streamflow.fraud-alerts"))
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )
        .build()
    )
    fraud_alerts.sink_to(kafka_alert_sink)

    # Side output: fraud alerts → PostgreSQL bronze
    jdbc_url = f"jdbc:postgresql://{pg_cfg['host']}:{pg_cfg.get('port', 5432)}/{pg_cfg['database']}"

    jdbc_alert_sink = JdbcSink.sink(
        BRONZE_RAW_FRAUD_ALERTS_INSERT,
        type_info=None,
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
            .with_batch_interval_ms(500)
            .with_batch_size(50)
            .with_max_retries(3)
            .build()
        ),
    )
    fraud_alerts.add_sink(jdbc_alert_sink)


def main(config: dict[str, Any]) -> None:
    """Entry point for the fraud detection job."""
    env = StreamExecutionEnvironment.get_execution_environment()

    flink_cfg = config.get("flink", {})
    env.enable_checkpointing(flink_cfg.get("checkpoint_interval_ms", 60000))
    env.set_parallelism(flink_cfg.get("parallelism", 2))

    build_fraud_detection_pipeline(env, config)
    env.execute("streamflow-fraud-detector")
