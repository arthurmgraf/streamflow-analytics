"""Airflow DAG: Silver → Gold transformation.

Runs hourly (after bronze_to_silver) to build dimensional model.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.sensors.external_task import ExternalTaskSensor

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="silver_to_gold",
    default_args=default_args,
    description="Build Gold dimensional model from Silver data",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "medallion", "gold"],
) as dag:
    wait_for_silver = ExternalTaskSensor(
        task_id="wait_for_silver",
        external_dag_id="bronze_to_silver",
        external_task_id="update_customer_stats",
        mode="reschedule",
        timeout=600,
        poke_interval=30,
    )

    build_gold = PostgresOperator(
        task_id="build_gold",
        postgres_conn_id="streamflow_postgres",
        sql="sql/transforms/silver_to_gold.sql",
    )

    wait_for_silver >> build_gold
