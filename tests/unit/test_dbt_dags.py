"""Tests for dbt Cosmos DAGs.

Validates DAG structure, task groups, and configuration
without requiring Airflow or Cosmos to be installed.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

DAGS_DIR = Path(__file__).resolve().parents[2] / "src" / "dags"

# --- Mock external dependencies before import ---


@pytest.fixture(autouse=True)
def _mock_airflow_and_cosmos(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock Airflow and Cosmos modules for DAG parsing."""
    mock_modules = {
        "airflow": MagicMock(),
        "airflow.models": MagicMock(),
        "airflow.sensors": MagicMock(),
        "airflow.sensors.external_task": MagicMock(),
        "airflow.providers": MagicMock(),
        "airflow.providers.postgres": MagicMock(),
        "airflow.providers.postgres.operators": MagicMock(),
        "airflow.providers.postgres.operators.postgres": MagicMock(),
        "airflow.utils": MagicMock(),
        "airflow.utils.task_group": MagicMock(),
        "cosmos": MagicMock(),
        "cosmos.constants": MagicMock(),
        "cosmos.profiles": MagicMock(),
    }
    for mod_name, mock in mock_modules.items():
        monkeypatch.setitem(sys.modules, mod_name, mock)


class TestDbtDagFiles:
    """Validate dbt DAG files exist and have correct structure."""

    @pytest.mark.parametrize(
        "dag_file",
        ["dbt_staging.py", "dbt_marts.py", "dbt_quality.py"],
    )
    def test_dag_file_exists(self, dag_file: str) -> None:
        path = DAGS_DIR / dag_file
        assert path.exists(), f"DAG file {dag_file} not found at {path}"

    @pytest.mark.parametrize(
        "dag_file",
        ["dbt_staging.py", "dbt_marts.py", "dbt_quality.py"],
    )
    def test_dag_file_valid_python(self, dag_file: str) -> None:
        path = DAGS_DIR / dag_file
        source = path.read_text(encoding="utf-8")
        ast.parse(source)  # Raises SyntaxError if invalid

    @pytest.mark.parametrize(
        ("dag_file", "expected_dag_id"),
        [
            ("dbt_staging.py", "dbt_staging"),
            ("dbt_marts.py", "dbt_marts"),
            ("dbt_quality.py", "dbt_quality"),
        ],
    )
    def test_dag_id_present(self, dag_file: str, expected_dag_id: str) -> None:
        path = DAGS_DIR / dag_file
        source = path.read_text(encoding="utf-8")
        assert f'dag_id="{expected_dag_id}"' in source

    @pytest.mark.parametrize(
        "dag_file",
        ["dbt_staging.py", "dbt_marts.py", "dbt_quality.py"],
    )
    def test_dag_imports_cosmos(self, dag_file: str) -> None:
        path = DAGS_DIR / dag_file
        source = path.read_text(encoding="utf-8")
        assert "from cosmos" in source, f"{dag_file} must import from cosmos"

    @pytest.mark.parametrize(
        "dag_file",
        ["dbt_staging.py", "dbt_marts.py", "dbt_quality.py"],
    )
    def test_dag_uses_dbt_task_group(self, dag_file: str) -> None:
        path = DAGS_DIR / dag_file
        source = path.read_text(encoding="utf-8")
        assert "DbtTaskGroup" in source, f"{dag_file} must use DbtTaskGroup"

    @pytest.mark.parametrize(
        "dag_file",
        ["dbt_staging.py", "dbt_marts.py", "dbt_quality.py"],
    )
    def test_dag_has_callbacks(self, dag_file: str) -> None:
        path = DAGS_DIR / dag_file
        source = path.read_text(encoding="utf-8")
        assert "on_failure_callback" in source


class TestOldDagsRemoved:
    """Verify deprecated DAGs are no longer present."""

    @pytest.mark.parametrize(
        "old_dag",
        ["bronze_to_silver.py", "silver_to_gold.py", "data_quality.py"],
    )
    def test_old_dag_removed(self, old_dag: str) -> None:
        path = DAGS_DIR / old_dag
        assert not path.exists(), f"Old DAG {old_dag} should be deleted (replaced by dbt)"


class TestDbtMartsDependency:
    """Verify dbt_marts waits for dbt_staging."""

    def test_marts_has_external_sensor(self) -> None:
        path = DAGS_DIR / "dbt_marts.py"
        source = path.read_text(encoding="utf-8")
        assert "ExternalTaskSensor" in source
        assert 'external_dag_id="dbt_staging"' in source


class TestMaintenanceDagPreserved:
    """Verify maintenance DAG was NOT deleted."""

    def test_maintenance_exists(self) -> None:
        path = DAGS_DIR / "maintenance.py"
        assert path.exists(), "maintenance.py should be preserved"
