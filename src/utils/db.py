"""PostgreSQL connection helper."""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import psycopg2
import psycopg2.extensions
import psycopg2.extras

logger = logging.getLogger(__name__)


def get_connection(config: dict[str, Any]) -> psycopg2.extensions.connection:
    """Create a PostgreSQL connection from config dict.

    Args:
        config: Must contain 'postgres' key with host, port, database, user.
                Password from 'postgres.password' or PGPASSWORD env var.

    Returns:
        psycopg2 connection object.
    """
    pg = config["postgres"]
    conn: psycopg2.extensions.connection = psycopg2.connect(
        host=pg["host"],
        port=pg.get("port", 5432),
        dbname=pg["database"],
        user=pg["user"],
        password=pg.get("password", ""),
    )
    conn.autocommit = False
    return conn


@contextmanager
def get_cursor(
    config: dict[str, Any],
    dict_cursor: bool = False,
) -> Generator[psycopg2.extensions.cursor, None, None]:
    """Context manager that yields a cursor and handles commit/rollback.

    Args:
        config: Database configuration dict.
        dict_cursor: If True, return rows as dicts.

    Yields:
        Database cursor.
    """
    conn = get_connection(config)
    cursor_factory = psycopg2.extras.RealDictCursor if dict_cursor else None
    try:
        with conn.cursor(cursor_factory=cursor_factory) as cur:
            yield cur
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
