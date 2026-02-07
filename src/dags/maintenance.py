"""Airflow DAG: Database maintenance.

Runs daily at 03:00. Parallel pruning via TaskGroup, callbacks, notification.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup

from src.dags.common.callbacks import on_failure_callback, on_success_callback

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "on_failure_callback": on_failure_callback,
    "on_success_callback": on_success_callback,
}

with DAG(
    dag_id="maintenance",
    default_args=default_args,
    description="Database maintenance: prune old data, vacuum, analyze",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "maintenance"],
    max_active_runs=1,
) as dag:
    with TaskGroup("pruning") as pruning:
        prune_bronze_transactions = PostgresOperator(
            task_id="prune_bronze_transactions",
            postgres_conn_id="streamflow_postgres",
            sql="""
                DELETE FROM bronze.raw_transactions
                WHERE ingested_at < NOW() - INTERVAL '30 days';
            """,
        )

        prune_bronze_alerts = PostgresOperator(
            task_id="prune_bronze_alerts",
            postgres_conn_id="streamflow_postgres",
            sql="""
                DELETE FROM bronze.raw_fraud_alerts
                WHERE detected_at < NOW() - INTERVAL '90 days';
            """,
        )

        prune_quality_logs = PostgresOperator(
            task_id="prune_quality_logs",
            postgres_conn_id="streamflow_postgres",
            sql="""
                DELETE FROM silver.quality_check_results
                WHERE checked_at < NOW() - INTERVAL '7 days';
            """,
        )

    with TaskGroup("vacuum") as vacuum:
        vacuum_bronze = PostgresOperator(
            task_id="vacuum_bronze",
            postgres_conn_id="streamflow_postgres",
            sql="""
                VACUUM ANALYZE bronze.raw_transactions;
                VACUUM ANALYZE bronze.raw_fraud_alerts;
            """,
        )

        vacuum_silver = PostgresOperator(
            task_id="vacuum_silver",
            postgres_conn_id="streamflow_postgres",
            sql="""
                VACUUM ANALYZE silver.clean_transactions;
                VACUUM ANALYZE silver.customers;
            """,
        )

    pruning >> vacuum
