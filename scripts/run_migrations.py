#!/usr/bin/env python3
"""Run SQL migrations against PostgreSQL in order.

Usage:
    python scripts/run_migrations.py --config-dir config --env dev
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any

from src.utils.config import load_config
from src.utils.db import get_cursor
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "sql" / "migrations"


def run_migrations(config: dict[str, Any]) -> None:
    """Execute all SQL migration files in order."""
    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))

    if not migration_files:
        logger.warning("No migration files found in %s", MIGRATIONS_DIR)
        return

    for migration_file in migration_files:
        logger.info("Running migration: %s", migration_file.name)
        sql = migration_file.read_text()

        with get_cursor(config) as cur:
            cur.execute(sql)

        logger.info("Completed: %s", migration_file.name)

    logger.info("All %d migrations completed successfully", len(migration_files))


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
