"""Airflow DAG: Bronze -> Silver transformation.

Runs hourly. Uses TaskGroups for validation, transformation, and post-validation.
Includes SLA, callbacks, and structured error handling.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup

from src.dags.common.callbacks import on_failure_callback, on_sla_miss_callback, on_success_callback

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": on_failure_callback,
    "on_success_callback": on_success_callback,
    "sla": timedelta(minutes=30),
}

with DAG(
    dag_id="bronze_to_silver",
    default_args=default_args,
    description="Transform raw Bronze data to cleaned Silver layer",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "medallion", "silver"],
    sla_miss_callback=on_sla_miss_callback,
    max_active_runs=1,
) as dag:
    with TaskGroup("pre_validation") as pre_validation:
        check_bronze_freshness = PostgresOperator(
            task_id="check_bronze_freshness",
            postgres_conn_id="streamflow_postgres",
            sql="""
                SELECT CASE
                    WHEN MAX(ingested_at) > NOW() - INTERVAL '2 hours'
                    THEN 1
                    ELSE 1/(SELECT 0)  -- Fail if no recent data
                END FROM bronze.raw_transactions;
            """,
        )

    with TaskGroup("transformation") as transformation:
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

    with TaskGroup("post_validation") as post_validation:
        check_silver_row_count = PostgresOperator(
            task_id="check_silver_row_count",
            postgres_conn_id="streamflow_postgres",
            sql="""
                SELECT CASE
                    WHEN COUNT(*) > 0 THEN 1
                    ELSE 1/(SELECT 0)
                END FROM silver.clean_transactions
                WHERE processed_at > NOW() - INTERVAL '2 hours';
            """,
        )

    pre_validation >> transformation >> post_validation
