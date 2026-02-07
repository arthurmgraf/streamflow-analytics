"""Unit tests for Dead Letter Queue utilities."""

from __future__ import annotations

import json

from src.flink_jobs.common.dlq import MAX_RAW_EVENT_SIZE, build_dlq_record


class TestBuildDlqRecord:
    """Tests for DLQ record construction."""

    def test_valid_record_structure(self) -> None:
        record = build_dlq_record(
            raw_event='{"bad": json}',
            error_type="JSONDecodeError",
            error_message="Expecting value",
            source_topic="transactions.raw",
            processor="transaction-processor",
        )
        parsed = json.loads(record)
        assert parsed["error_type"] == "JSONDecodeError"
        assert parsed["error_message"] == "Expecting value"
        assert parsed["source_topic"] == "transactions.raw"
        assert parsed["processor"] == "transaction-processor"
        assert parsed["raw_event"] == '{"bad": json}'
        assert parsed["truncated"] is False
        assert "timestamp" in parsed

    def test_large_event_truncated(self) -> None:
        large_event = "x" * (MAX_RAW_EVENT_SIZE + 500)
        record = build_dlq_record(
            raw_event=large_event,
            error_type="ValueError",
            error_message="Event too large",
            source_topic="transactions.raw",
        )
        parsed = json.loads(record)
        assert parsed["truncated"] is True
        assert len(parsed["raw_event"]) == MAX_RAW_EVENT_SIZE
        assert parsed["raw_event_length"] == MAX_RAW_EVENT_SIZE + 500

    def test_small_event_not_truncated(self) -> None:
        record = build_dlq_record(
            raw_event="small event",
            error_type="ValueError",
            error_message="Bad format",
            source_topic="transactions.raw",
        )
        parsed = json.loads(record)
        assert parsed["truncated"] is False
        assert parsed["raw_event"] == "small event"

    def test_default_processor(self) -> None:
        record = build_dlq_record(
            raw_event="test",
            error_type="Error",
            error_message="msg",
            source_topic="topic",
        )
        parsed = json.loads(record)
        assert parsed["processor"] == "unknown"

    def test_output_is_valid_json(self) -> None:
        record = build_dlq_record(
            raw_event='{"nested": {"data": true}}',
            error_type="ValidationError",
            error_message="Missing field",
            source_topic="transactions.raw",
            processor="fraud-detector",
        )
        parsed = json.loads(record)
        assert isinstance(parsed, dict)
        assert len(parsed) == 8

    def test_timestamp_is_numeric(self) -> None:
        record = build_dlq_record(
            raw_event="test",
            error_type="Error",
            error_message="msg",
            source_topic="topic",
        )
        parsed = json.loads(record)
        assert isinstance(parsed["timestamp"], float)
