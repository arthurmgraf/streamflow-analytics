"""Structured JSON logging setup."""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=UTC
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info and record.exc_info[1] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Include extra fields passed via `extra={}`
        for key in ("component", "job_name", "transaction_id", "customer_id"):
            value = getattr(record, key, None)
            if value is not None:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


def setup_logging(
    level: int | str = logging.INFO,
    json_output: bool = True,
) -> None:
    """Configure root logger with structured JSON output.

    Args:
        level: Logging level.
        json_output: If True, use JSON formatter. Otherwise use simple format.
    """
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers to avoid duplicates
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if json_output:
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(name)s — %(message)s")
        )

    root.addHandler(handler)

    # Reduce noise from third-party libs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("kafka").setLevel(logging.WARNING)
