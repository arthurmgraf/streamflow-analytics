"""Kafka producer wrapper for event generation."""

from __future__ import annotations

import json
import logging
from typing import Any

from confluent_kafka import Producer

from src.models.transaction import Transaction

logger = logging.getLogger(__name__)


class StreamFlowProducer:
    """Kafka producer for StreamFlow transaction events."""

    def __init__(self, config: dict[str, Any]) -> None:
        kafka_cfg = config["kafka"]
        self._producer = Producer({
            "bootstrap.servers": kafka_cfg["bootstrap_servers"],
            "client.id": "streamflow-generator",
            "acks": "all",
            "retries": 3,
            "linger.ms": 10,
            "batch.size": 16384,
        })
        self._topic = kafka_cfg["topics"]["transactions"]
        self._sent = 0
        self._errors = 0

    def send(self, txn: Transaction) -> None:
        """Send a transaction to Kafka.

        Args:
            txn: Transaction to produce.
        """
        try:
            self._producer.produce(
                topic=self._topic,
                key=txn.to_kafka_key().encode("utf-8"),
                value=json.dumps(txn.to_json_dict(), default=str).encode("utf-8"),
                callback=self._delivery_callback,
            )
            self._sent += 1
            # Trigger delivery reports periodically
            if self._sent % 100 == 0:
                self._producer.poll(0)
        except BufferError:
            logger.warning("Producer buffer full, flushing...")
            self._producer.flush(timeout=5)
            # Retry
            self._producer.produce(
                topic=self._topic,
                key=txn.to_kafka_key().encode("utf-8"),
                value=json.dumps(txn.to_json_dict(), default=str).encode("utf-8"),
                callback=self._delivery_callback,
            )

    def flush(self, timeout: float = 10.0) -> None:
        """Flush remaining messages."""
        remaining = self._producer.flush(timeout=timeout)
        if remaining > 0:
            logger.warning("Failed to flush %d messages", remaining)

    def _delivery_callback(self, err: Any, msg: Any) -> None:
        if err is not None:
            self._errors += 1
            logger.error("Delivery failed: %s", err)

    @property
    def stats(self) -> dict[str, int]:
        """Return producer statistics."""
        return {"sent": self._sent, "errors": self._errors}
