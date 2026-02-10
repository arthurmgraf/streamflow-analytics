#!/usr/bin/env python3
"""Run SQL migrations against PostgreSQL with tracking.

Maintains a schema_migrations table to avoid re-running migrations.

Usage:
    python scripts/run_migrations.py --config-dir config --env dev
"""

from __future__ import annotations

import argparse
import hashlib
import logging
from pathlib import Path
from typing import Any

from src.utils.config import load_config
from src.utils.db import get_cursor
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "sql" / "migrations"

_TRACKING_DDL = """
CREATE TABLE IF NOT EXISTS public.schema_migrations (
    version     TEXT PRIMARY KEY,
    filename    TEXT NOT NULL,
    checksum    TEXT NOT NULL,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def _ensure_tracking_table(config: dict[str, Any]) -> None:
    with get_cursor(config) as cur:
        cur.execute(_TRACKING_DDL)


def _applied_versions(config: dict[str, Any]) -> set[str]:
    with get_cursor(config) as cur:
        cur.execute("SELECT version FROM public.schema_migrations ORDER BY version")
        return {row[0] for row in cur.fetchall()}


def _file_checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def run_migrations(config: dict[str, Any]) -> None:
    """Execute unapplied SQL migration files in order."""
    _ensure_tracking_table(config)
    applied = _applied_versions(config)

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not migration_files:
        logger.warning("No migration files found in %s", MIGRATIONS_DIR)
        return

    pending = [f for f in migration_files if f.stem not in applied]
    if not pending:
        logger.info("All %d migrations already applied", len(migration_files))
        return

    for migration_file in pending:
        version = migration_file.stem
        checksum = _file_checksum(migration_file)
        logger.info("Running migration: %s", migration_file.name)

        sql = migration_file.read_text()
        with get_cursor(config) as cur:
            cur.execute(sql)
            cur.execute(
                "INSERT INTO public.schema_migrations (version, filename, checksum) "
                "VALUES (%s, %s, %s)",
                (version, migration_file.name, checksum),
            )

        logger.info("Completed: %s (checksum: %s)", migration_file.name, checksum)

    logger.info(
        "Applied %d of %d migrations", len(pending), len(migration_files),
    )


def main() -> None:
    """Run the migration script."""
    parser = argparse.ArgumentParser(description="Run SQL migrations")
    parser.add_argument("--config-dir", default="config")
    parser.add_argument("--env", default="dev")
    args = parser.parse_args()

    config = load_config(config_dir=args.config_dir, env=args.env)
    setup_logging()

    run_migrations(config)


if __name__ == "__main__":
    main()
