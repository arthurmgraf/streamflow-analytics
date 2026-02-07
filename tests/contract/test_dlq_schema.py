"""Contract tests for Dead Letter Queue record schema.

These tests define the schema contract between DLQ producers (Flink jobs)
and DLQ consumers (monitoring, reprocessing pipelines).

Contract guarantees:
    - DLQ records contain all required metadata fields
    - Original event is preserved (possibly truncated)
    - Truncation is correctly flagged
    - Output is always valid JSON
"""

from __future__ import annotations

import json

import pytest

from src.flink_jobs.common.dlq import MAX_RAW_EVENT_SIZE, build_dlq_record

pytestmark = pytest.mark.contract

DLQ_REQUIRED_FIELDS = {
    "timestamp", "error_type", "error_message", "source_topic",
    "processor", "raw_event", "truncated", "raw_event_length",
}


class TestDLQSchemaContract:
    """Contract: DLQ record structure."""

    def test_required_fields_present(self) -> None:
        record = build_dlq_record(
            raw_event="bad data",
            error_type="JSONDecodeError",
            error_message="Expecting value",
            source_topic="streamflow.transactions",
            processor="fraud-detector",
        )
        parsed = json.loads(record)
        assert DLQ_REQUIRED_FIELDS.issubset(parsed.keys())

    def test_output_is_valid_json(self) -> None:
        record = build_dlq_record(
            raw_event="anything",
            error_type="ValueError",
            error_message="test",
            source_topic="test.topic",
        )
        parsed = json.loads(record)
        assert isinstance(parsed, dict)

    def test_default_processor(self) -> None:
        record = build_dlq_record(
            raw_event="data",
            error_type="Error",
            error_message="msg",
            source_topic="topic",
        )
        parsed = json.loads(record)
        assert parsed["processor"] == "unknown"

    def test_raw_event_preserved(self) -> None:
        original = '{"key": "value", "nested": {"a": 1}}'
        record = build_dlq_record(
            raw_event=original,
            error_type="ValidationError",
            error_message="missing field",
            source_topic="streamflow.transactions",
        )
        parsed = json.loads(record)
        assert parsed["raw_event"] == original
        assert parsed["truncated"] is False
        assert parsed["raw_event_length"] == len(original)

    def test_large_event_truncated(self) -> None:
        large_event = "x" * (MAX_RAW_EVENT_SIZE + 500)
        record = build_dlq_record(
            raw_event=large_event,
            error_type="SizeError",
            error_message="too large",
            source_topic="test.topic",
        )
        parsed = json.loads(record)
        assert parsed["truncated"] is True
        assert len(parsed["raw_event"]) == MAX_RAW_EVENT_SIZE
        assert parsed["raw_event_length"] == len(large_event)

    def test_exact_max_size_not_truncated(self) -> None:
        exact_event = "y" * MAX_RAW_EVENT_SIZE
        record = build_dlq_record(
            raw_event=exact_event,
            error_type="Error",
            error_message="test",
            source_topic="test.topic",
        )
        parsed = json.loads(record)
        assert parsed["truncated"] is False

    def test_timestamp_is_numeric(self) -> None:
        record = build_dlq_record(
            raw_event="data",
            error_type="Error",
            error_message="msg",
            source_topic="topic",
        )
        parsed = json.loads(record)
        assert isinstance(parsed["timestamp"], (int, float))
        assert parsed["timestamp"] > 0

    def test_error_metadata_preserved(self) -> None:
        record = build_dlq_record(
            raw_event="data",
            error_type="CustomException",
            error_message="detailed error message",
            source_topic="streamflow.transactions",
            processor="fraud-detector-v2",
        )
        parsed = json.loads(record)
        assert parsed["error_type"] == "CustomException"
        assert parsed["error_message"] == "detailed error message"
        assert parsed["source_topic"] == "streamflow.transactions"
        assert parsed["processor"] == "fraud-detector-v2"
