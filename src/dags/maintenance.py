"""Airflow DAG: Database maintenance.

Runs daily at 03:00 to prune old data and vacuum tables.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="maintenance",
    default_args=default_args,
    description="Database maintenance: prune old data, vacuum, analyze",
    schedule="0 3 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "maintenance"],
) as dag:
    prune_bronze = PostgresOperator(
        task_id="prune_bronze_older_than_30d",
        postgres_conn_id="streamflow_postgres",
        sql="""
            DELETE FROM bronze.raw_transactions
            WHERE ingested_at < NOW() - INTERVAL '30 days';

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

    vacuum_analyze = PostgresOperator(
        task_id="vacuum_analyze",
        postgres_conn_id="streamflow_postgres",
        sql="""
            VACUUM ANALYZE bronze.raw_transactions;
            VACUUM ANALYZE bronze.raw_fraud_alerts;
            VACUUM ANALYZE silver.clean_transactions;
            VACUUM ANALYZE silver.customers;
        """,
    )

    prune_bronze >> prune_quality_logs >> vacuum_analyze
