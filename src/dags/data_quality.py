"""Airflow DAG: Data quality checks.

Runs every 15 minutes. Separate tasks per check type for granular alerting.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup

from src.dags.common.callbacks import on_failure_callback, on_sla_miss_callback

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "on_failure_callback": on_failure_callback,
    "sla": timedelta(minutes=10),
}

with (
    DAG(
        dag_id="data_quality",
        default_args=default_args,
        description="Run data quality checks across all layers",
        schedule="*/15 * * * *",
        start_date=datetime(2026, 1, 1),
        catchup=False,
        tags=["streamflow", "quality"],
        sla_miss_callback=on_sla_miss_callback,
        max_active_runs=1,
    ) as dag,
    TaskGroup("quality_checks") as quality_checks,
):
    check_null_rate = PostgresOperator(
        task_id="check_null_rate",
        postgres_conn_id="streamflow_postgres",
        sql="sql/quality/check_null_rate.sql",
    )

    check_duplicates = PostgresOperator(
        task_id="check_duplicates",
        postgres_conn_id="streamflow_postgres",
        sql="sql/quality/check_duplicates.sql",
    )

    check_freshness = PostgresOperator(
        task_id="check_freshness",
        postgres_conn_id="streamflow_postgres",
        sql="sql/quality/check_freshness.sql",
    )

    check_amounts = PostgresOperator(
        task_id="check_amounts",
        postgres_conn_id="streamflow_postgres",
        sql="sql/quality/check_amounts.sql",
    )
