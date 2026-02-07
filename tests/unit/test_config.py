"""Unit tests for configuration loading."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.config import _deep_merge, load_config


class TestDeepMerge:
    """Tests for _deep_merge utility."""

    def test_simple_merge(self) -> None:
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        result = _deep_merge(base, override)
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_nested_merge(self) -> None:
        base = {"kafka": {"host": "localhost", "port": 9092}}
        override = {"kafka": {"host": "prod-server"}}
        result = _deep_merge(base, override)
        assert result == {"kafka": {"host": "prod-server", "port": 9092}}

    def test_deep_nested_merge(self) -> None:
        base = {"a": {"b": {"c": 1, "d": 2}}}
        override = {"a": {"b": {"c": 10}}}
        result = _deep_merge(base, override)
        assert result == {"a": {"b": {"c": 10, "d": 2}}}

    def test_override_replaces_non_dict(self) -> None:
        base = {"a": "string_value"}
        override = {"a": {"nested": True}}
        result = _deep_merge(base, override)
        assert result == {"a": {"nested": True}}

    def test_empty_override(self) -> None:
        base = {"a": 1}
        result = _deep_merge(base, {})
        assert result == {"a": 1}

    def test_empty_base(self) -> None:
        override = {"a": 1}
        result = _deep_merge({}, override)
        assert result == {"a": 1}

    def test_base_not_mutated(self) -> None:
        base = {"a": 1, "b": 2}
        _deep_merge(base, {"a": 99})
        assert base == {"a": 1, "b": 2}


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_default_config(self, config_dir: Path) -> None:
        config = load_config(config_dir=config_dir, env="nonexistent")
        assert config["project"]["name"] == "streamflow-analytics"
        assert config["kafka"]["topics"]["transactions"] == "transactions.raw"

    def test_dev_overrides_applied(self, config_dir: Path) -> None:
        config = load_config(config_dir=config_dir, env="dev")
        assert config["kafka"]["bootstrap_servers"] == "localhost:9092"
        assert config["postgres"]["host"] == "localhost"

    def test_dev_preserves_defaults(self, config_dir: Path) -> None:
        config = load_config(config_dir=config_dir, env="dev")
        # Topics come from default.yaml, not overridden in dev.yaml
        assert config["kafka"]["topics"]["transactions"] == "transactions.raw"

    def test_env_injected_in_config(self, config_dir: Path) -> None:
        config = load_config(config_dir=config_dir, env="dev")
        assert config["project"]["env"] == "dev"

    def test_env_from_environment_variable(self, config_dir: Path) -> None:
        with patch.dict(os.environ, {"STREAMFLOW_ENV": "dev"}):
            config = load_config(config_dir=config_dir)
            assert config["project"]["env"] == "dev"

    def test_missing_default_config_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError, match="Default config not found"):
            load_config(config_dir=tmp_path)

    def test_fraud_rules_config(self, config_dir: Path) -> None:
        config = load_config(config_dir=config_dir, env="dev")
        rules = config["fraud_rules"]
        assert rules["high_value"]["enabled"] is True
        assert rules["high_value"]["multiplier"] == 3.0
        assert rules["velocity"]["max_count"] == 5
