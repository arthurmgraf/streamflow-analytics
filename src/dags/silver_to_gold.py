"""Airflow DAG: Silver -> Gold transformation.

Runs hourly after bronze_to_silver. TaskGroups for dimensions, facts, and aggregates.
Each dimension/fact is a separate task for granular monitoring.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.utils.task_group import TaskGroup

from src.dags.common.callbacks import on_failure_callback, on_sla_miss_callback, on_success_callback

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": on_failure_callback,
    "on_success_callback": on_success_callback,
    "sla": timedelta(minutes=45),
}

with DAG(
    dag_id="silver_to_gold",
    default_args=default_args,
    description="Build Gold dimensional model from Silver data",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "medallion", "gold"],
    sla_miss_callback=on_sla_miss_callback,
    max_active_runs=1,
) as dag:
    wait_for_silver = ExternalTaskSensor(
        task_id="wait_for_silver",
        external_dag_id="bronze_to_silver",
        external_task_id="post_validation.check_silver_row_count",
        mode="reschedule",
        timeout=600,
        poke_interval=30,
    )

    with TaskGroup("dimensions") as dimensions:
        upsert_dim_customer = PostgresOperator(
            task_id="upsert_dim_customer",
            postgres_conn_id="streamflow_postgres",
            sql="sql/transforms/gold/upsert_dim_customer.sql",
        )

        upsert_dim_store = PostgresOperator(
            task_id="upsert_dim_store",
            postgres_conn_id="streamflow_postgres",
            sql="sql/transforms/gold/upsert_dim_store.sql",
        )

    with TaskGroup("facts") as facts:
        load_fact_transactions = PostgresOperator(
            task_id="load_fact_transactions",
            postgres_conn_id="streamflow_postgres",
            sql="sql/transforms/gold/load_fact_transactions.sql",
        )

        load_fact_fraud_alerts = PostgresOperator(
            task_id="load_fact_fraud_alerts",
            postgres_conn_id="streamflow_postgres",
            sql="sql/transforms/gold/load_fact_fraud_alerts.sql",
        )

    with TaskGroup("aggregates") as aggregates:
        refresh_hourly_sales = PostgresOperator(
            task_id="refresh_hourly_sales",
            postgres_conn_id="streamflow_postgres",
            sql="sql/transforms/gold/refresh_hourly_sales.sql",
        )

        refresh_daily_fraud = PostgresOperator(
            task_id="refresh_daily_fraud",
            postgres_conn_id="streamflow_postgres",
            sql="sql/transforms/gold/refresh_daily_fraud.sql",
        )

    wait_for_silver >> dimensions >> facts >> aggregates
