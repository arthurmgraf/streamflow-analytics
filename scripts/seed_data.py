#!/usr/bin/env python3
"""Seed reference data into PostgreSQL Silver layer.

Generates customers, stores, and products, then inserts into silver schema.

Usage:
    python scripts/seed_data.py --config-dir config --env dev
"""

from __future__ import annotations

import argparse
import logging
from typing import Any

from src.generators.customer_generator import generate_customers
from src.generators.store_generator import generate_stores
from src.utils.config import load_config
from src.utils.db import get_cursor
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def seed_customers(config: dict[str, Any], count: int, seed: int) -> int:
    """Seed customer profiles into silver.customers."""
    customers = generate_customers(count, seed=seed)
    with get_cursor(config) as cur:
        for c in customers:
            cur.execute(
                """
                INSERT INTO silver.customers
                    (customer_id, name, email, city, state, risk_profile)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO NOTHING
                """,
                (c.customer_id, c.name, c.email, c.city, c.state, c.risk_profile.value),
            )
    return len(customers)


def seed_stores(config: dict[str, Any], count: int, seed: int) -> int:
    """Seed store data into silver.stores."""
    stores = generate_stores(count, seed=seed)
    with get_cursor(config) as cur:
        for s in stores:
            cur.execute(
                """
                INSERT INTO silver.stores
                    (store_id, name, city, state, latitude, longitude, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (store_id) DO NOTHING
                """,
                (s.store_id, s.name, s.city, s.state, s.latitude, s.longitude, s.category),
            )
    return len(stores)


def seed_products(config: dict[str, Any], count: int, seed: int) -> int:
    """Seed product catalog into silver.products."""
    import random

    rng = random.Random(seed)
    categories = [
        "electronics", "clothing", "food", "pharmacy", "supermarket",
        "furniture", "sports", "books", "cosmetics", "automotive",
    ]
    with get_cursor(config) as cur:
        for i in range(count):
            cat = rng.choice(categories)
            price = round(rng.uniform(10, 5000), 2)
            cur.execute(
                """
                INSERT INTO silver.products (product_id, name, category, price)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING
                """,
                (f"prod-{i:04d}", f"Produto {cat.title()} {i}", cat, price),
            )
    return count


def main() -> None:
    """Run the seed script."""
    parser = argparse.ArgumentParser(description="Seed reference data into PostgreSQL")
    parser.add_argument("--config-dir", default="config")
    parser.add_argument("--env", default="dev")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    config = load_config(config_dir=args.config_dir, env=args.env)
    setup_logging()

    gen_cfg = config.get("generator", {})

    n_customers = seed_customers(config, gen_cfg.get("num_customers", 100), args.seed)
    logger.info("Seeded %d customers", n_customers)

    n_stores = seed_stores(config, gen_cfg.get("num_stores", 10), args.seed)
    logger.info("Seeded %d stores", n_stores)

    n_products = seed_products(config, gen_cfg.get("num_products", 50), args.seed)
    logger.info("Seeded %d products", n_products)

    logger.info("Seed complete!")


if __name__ == "__main__":
    main()
