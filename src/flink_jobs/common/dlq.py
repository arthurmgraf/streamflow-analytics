"""Dead Letter Queue utilities for malformed event handling.

Instead of silently dropping malformed events (logger.warning + return None),
we capture them with full metadata for debugging and reprocessing.
"""

from __future__ import annotations

import json
import time
from typing import Any

MAX_RAW_EVENT_SIZE = 10_000


def build_dlq_record(
    raw_event: str,
    error_type: str,
    error_message: str,
    source_topic: str,
    processor: str = "unknown",
) -> str:
    """Build a DLQ record wrapping the original event with error metadata.

    Args:
        raw_event: The original malformed event string.
        error_type: Exception class name (e.g., "JSONDecodeError").
        error_message: Human-readable error description.
        source_topic: Kafka topic the event came from.
        processor: Name of the Flink job that rejected the event.

    Returns:
        JSON string ready to publish to the DLQ topic.
    """
    truncated = raw_event[:MAX_RAW_EVENT_SIZE]
    was_truncated = len(raw_event) > MAX_RAW_EVENT_SIZE

    record: dict[str, Any] = {
        "timestamp": time.time(),
        "error_type": error_type,
        "error_message": error_message,
        "source_topic": source_topic,
        "processor": processor,
        "raw_event": truncated,
        "truncated": was_truncated,
        "raw_event_length": len(raw_event),
    }
    return json.dumps(record, default=str)
