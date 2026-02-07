"""Shared Airflow callbacks for StreamFlow DAGs.

Provides standardized failure, success, and SLA miss handlers
that can be reused across all production DAGs.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("streamflow.dags")


def on_failure_callback(context: dict[str, Any]) -> None:
    """Log structured failure info for alerting integration."""
    task_instance = context.get("task_instance")
    dag_id = context.get("dag", {})
    exception = context.get("exception", "Unknown")
    logger.error(
        "TASK_FAILED | dag=%s | task=%s | execution_date=%s | error=%s",
        getattr(dag_id, "dag_id", "unknown"),
        getattr(task_instance, "task_id", "unknown"),
        context.get("execution_date", "unknown"),
        str(exception)[:500],
    )


def on_success_callback(context: dict[str, Any]) -> None:
    """Log structured success info for observability."""
    task_instance = context.get("task_instance")
    dag_id = context.get("dag", {})
    logger.info(
        "TASK_SUCCESS | dag=%s | task=%s | duration=%s",
        getattr(dag_id, "dag_id", "unknown"),
        getattr(task_instance, "task_id", "unknown"),
        getattr(task_instance, "duration", "unknown"),
    )


def on_sla_miss_callback(
    dag: Any,
    task_list: str,
    blocking_task_list: str,
    slas: list[Any],
    blocking_tis: list[Any],
) -> None:
    """Log SLA miss for alerting."""
    dag_id = getattr(dag, "dag_id", "unknown")
    logger.warning(
        "SLA_MISS | dag=%s | tasks=%s | blocking=%s",
        dag_id,
        task_list,
        blocking_task_list,
    )
