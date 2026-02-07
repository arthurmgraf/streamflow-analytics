"""Kafka SerDe utilities for PyFlink jobs.

Supports schema versioning for forward-compatible event parsing.
Unknown schema versions are parsed with best-effort (log warning, attempt parse).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from src.models.fraud_alert import FraudAlert
from src.models.transaction import Transaction

logger = logging.getLogger(__name__)

CURRENT_SCHEMA_VERSION = 1


def deserialize_transaction(raw: str) -> Transaction | None:
    """Deserialize JSON string to Transaction model.

    Supports schema versioning:
        - v1 (current): Standard Transaction fields
        - Unknown versions: Best-effort parse with warning

    Returns None for malformed events.
    """
    try:
        data: dict[str, Any] = json.loads(raw)
        version = data.pop("schema_version", CURRENT_SCHEMA_VERSION)
        if version > CURRENT_SCHEMA_VERSION:
            logger.warning(
                "Unknown schema version %d (current=%d), attempting parse",
                version,
                CURRENT_SCHEMA_VERSION,
            )
        return Transaction(**data)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to deserialize transaction: %s", raw[:200])
        return None


def serialize_transaction(txn: Transaction) -> str:
    """Serialize Transaction to JSON string for Kafka."""
    return json.dumps(txn.to_json_dict(), default=str)


def serialize_fraud_alert(alert: FraudAlert) -> str:
    """Serialize FraudAlert to JSON string for Kafka."""
    return json.dumps(alert.to_json_dict(), default=str)


def deserialize_fraud_alert(raw: str) -> FraudAlert | None:
    """Deserialize JSON string to FraudAlert model.

    Returns None for malformed events.
    """
    try:
        data: dict[str, Any] = json.loads(raw)
        return FraudAlert(**data)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to deserialize fraud alert: %s", raw[:200])
        return None
