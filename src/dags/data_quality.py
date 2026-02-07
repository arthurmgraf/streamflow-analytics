"""Airflow DAG: Data quality checks.

Runs every 15 minutes to validate data freshness, nulls, duplicates.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="data_quality",
    default_args=default_args,
    description="Run data quality checks across all layers",
    schedule="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "quality"],
) as dag:
    run_quality_checks = PostgresOperator(
        task_id="run_quality_checks",
        postgres_conn_id="streamflow_postgres",
        sql="sql/quality/quality_checks.sql",
    )
