"""Airflow DAG: Bronze → Silver transformation.

Runs hourly to transform raw Bronze data into cleaned Silver layer.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="bronze_to_silver",
    default_args=default_args,
    description="Transform raw Bronze data to cleaned Silver layer",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "medallion", "silver"],
) as dag:
    transform_transactions = PostgresOperator(
        task_id="transform_transactions",
        postgres_conn_id="streamflow_postgres",
        sql="sql/transforms/bronze_to_silver.sql",
    )

    update_customer_stats = PostgresOperator(
        task_id="update_customer_stats",
        postgres_conn_id="streamflow_postgres",
        sql="sql/transforms/update_customer_stats.sql",
    )

    transform_transactions >> update_customer_stats
