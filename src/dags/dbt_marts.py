"""Airflow DAG: dbt marts transforms via Astronomer Cosmos.

Replaces silver_to_gold DAG. Runs intermediate + marts models after staging
completes. Uses ExternalTaskSensor to wait for dbt_staging DAG.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.sensors.external_task import ExternalTaskSensor
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import InvocationMode
from cosmos.profiles import PostgresUserPasswordProfileMapping

from src.dags.common.callbacks import on_failure_callback, on_sla_miss_callback, on_success_callback

DBT_PROJECT_PATH = Path("/opt/airflow/dbt")

profile_config = ProfileConfig(
    profile_name="streamflow",
    target_name="prod",
    profile_mapping=PostgresUserPasswordProfileMapping(
        conn_id="streamflow_postgres",
        profile_args={"schema": "gold"},
    ),
)

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
    dag_id="dbt_marts",
    default_args=default_args,
    description="dbt marts: Silver -> Gold via Cosmos DbtTaskGroup",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "dbt", "marts", "medallion"],
    sla_miss_callback=on_sla_miss_callback,
    max_active_runs=1,
) as dag:
    wait_for_staging = ExternalTaskSensor(
        task_id="wait_for_staging",
        external_dag_id="dbt_staging",
        mode="reschedule",
        timeout=600,
        poke_interval=30,
    )

    intermediate_and_marts = DbtTaskGroup(
        group_id="marts",
        project_config=ProjectConfig(dbt_project_path=str(DBT_PROJECT_PATH)),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            invocation_mode=InvocationMode.SUBPROCESS,
        ),
        render_config=RenderConfig(
            select=["path:models/intermediate", "path:models/marts"],
        ),
        operator_args={"install_deps": True},
    )

    wait_for_staging >> intermediate_and_marts
