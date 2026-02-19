"""Airflow DAG: dbt data quality tests via Astronomer Cosmos.

Replaces data_quality DAG. Runs dbt test (schema tests + singular tests)
every 15 minutes for continuous data quality monitoring.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig
from cosmos.constants import InvocationMode
from cosmos.profiles import PostgresUserPasswordProfileMapping

from src.dags.common.callbacks import on_failure_callback, on_sla_miss_callback

DBT_PROJECT_PATH = Path("/opt/airflow/dbt")

profile_config = ProfileConfig(
    profile_name="streamflow",
    target_name="prod",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="streamflow_postgres",
        profile_args={"schema": "silver"},
    ),
)

default_args = {
    "owner": "streamflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "on_failure_callback": on_failure_callback,
    "sla": timedelta(minutes=10),
}

with DAG(
    dag_id="dbt_quality",
    default_args=default_args,
    description="dbt data quality: schema tests + singular tests via Cosmos",
    schedule="*/15 * * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "dbt", "quality"],
    sla_miss_callback=on_sla_miss_callback,
    max_active_runs=1,
) as dag:
    quality_tests = DbtTaskGroup(
        group_id="quality",
        project_config=ProjectConfig(dbt_project_path=str(DBT_PROJECT_PATH)),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            invocation_mode=InvocationMode.SUBPROCESS,
        ),
        operator_args={
            "install_deps": True,
            "dbt_cmd_flags": ["--select", "test_type:singular"],
        },
    )
