"""Airflow DAG: dbt staging transforms via Astronomer Cosmos.

Replaces bronze_to_silver DAG. Each dbt model runs as a separate Airflow task,
providing per-model visibility, retries, and lineage in the Airflow UI.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
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
        profile_args={"schema": "silver"},
    ),
)

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
    dag_id="dbt_staging",
    default_args=default_args,
    description="dbt staging: Bronze -> Silver via Cosmos DbtTaskGroup",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["streamflow", "dbt", "staging", "medallion"],
    sla_miss_callback=on_sla_miss_callback,
    max_active_runs=1,
) as dag:
    staging = DbtTaskGroup(
        group_id="staging",
        project_config=ProjectConfig(dbt_project_path=str(DBT_PROJECT_PATH)),
        profile_config=profile_config,
        execution_config=ExecutionConfig(
            invocation_mode=InvocationMode.SUBPROCESS,
        ),
        render_config=RenderConfig(
            select=["path:models/staging"],
        ),
        operator_args={"install_deps": True},
    )
