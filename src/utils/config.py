"""YAML configuration loader with environment overrides."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

_ENV_VAR_PATTERN = re.compile(r"\$\{(\w+)(?::-(.*?))?\}")


def _expand_env_vars(value: Any) -> Any:
    """Expand ${VAR:-default} patterns in string values."""
    if isinstance(value, str):
        def _replace(match: re.Match[str]) -> str:
            var_name = match.group(1)
            default = match.group(2) if match.group(2) is not None else ""
            return os.environ.get(var_name, default)
        return _ENV_VAR_PATTERN.sub(_replace, value)
    if isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    return value


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge override dict into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config(
    config_dir: str | Path | None = None,
    env: str | None = None,
) -> dict[str, Any]:
    """Load configuration from YAML files.

    Loads default.yaml first, then merges environment-specific overrides.

    Args:
        config_dir: Path to config directory. Defaults to <project_root>/config.
        env: Environment name (e.g. 'dev', 'prod'). Defaults to
             STREAMFLOW_ENV env var, or 'dev'.

    Returns:
        Merged configuration dictionary.
    """
    if config_dir is None:
        config_dir = Path(__file__).resolve().parent.parent.parent / "config"
    config_dir = Path(config_dir)

    env = env or os.getenv("STREAMFLOW_ENV", "dev")

    # Load default config
    default_path = config_dir / "default.yaml"
    if not default_path.exists():
        msg = f"Default config not found: {default_path}"
        raise FileNotFoundError(msg)

    with open(default_path) as f:
        config: dict[str, Any] = yaml.safe_load(f) or {}

    # Merge environment overrides
    env_path = config_dir / f"{env}.yaml"
    if env_path.exists():
        with open(env_path) as f:
            env_config: dict[str, Any] = yaml.safe_load(f) or {}
        config = _deep_merge(config, env_config)

    # Expand environment variables (${VAR:-default} syntax)
    config = _expand_env_vars(config)

    # Inject environment name
    config.setdefault("project", {})
    config["project"]["env"] = env

    return config
