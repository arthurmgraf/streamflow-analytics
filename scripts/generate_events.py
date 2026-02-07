#!/usr/bin/env python3
"""CLI for generating and producing synthetic transaction events to Kafka.

Usage:
    python scripts/generate_events.py --config config/default.yaml
    python scripts/generate_events.py --events-per-second 50 --duration 60
"""

from __future__ import annotations

import argparse
import logging
import time

from src.generators.customer_generator import generate_customers
from src.generators.fraud_patterns import FraudInjector
from src.generators.kafka_producer import StreamFlowProducer
from src.generators.store_generator import generate_stores
from src.generators.transaction_generator import TransactionGenerator
from src.utils.config import load_config
from src.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Run the event generator."""
    parser = argparse.ArgumentParser(description="StreamFlow event generator")
    parser.add_argument("--config-dir", default="config", help="Config directory")
    parser.add_argument("--env", default="dev", help="Environment (dev/prod)")
    parser.add_argument("--events-per-second", type=int, help="Override EPS")
    parser.add_argument("--duration", type=int, default=0, help="Duration in seconds (0=infinite)")
    parser.add_argument("--dry-run", action="store_true", help="Generate but don't send to Kafka")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    args = parser.parse_args()

    config = load_config(config_dir=args.config_dir, env=args.env)
    setup_logging(level=config.get("logging", {}).get("level", "INFO"))

    gen_cfg = config.get("generator", {})
    eps = args.events_per_second or gen_cfg.get("events_per_second", 10)
    fraud_rate = gen_cfg.get("fraud_rate", 0.02)

    # Generate reference data
    customers = generate_customers(gen_cfg.get("num_customers", 100), seed=args.seed)
    stores = generate_stores(gen_cfg.get("num_stores", 10), seed=args.seed)

    logger.info(
        "Generated %d customers, %d stores (fraud_rate=%.2f, eps=%d)",
        len(customers),
        len(stores),
        fraud_rate,
        eps,
    )

    txn_gen = TransactionGenerator(customers, stores, seed=args.seed)
    fraud_injector = FraudInjector(customers, stores, fraud_rate=fraud_rate, seed=args.seed)

    producer = None
    if not args.dry_run:
        producer = StreamFlowProducer(config)

    start_time = time.time()
    total_sent = 0
    total_fraud = 0
    interval = 1.0 / eps

    try:
        while True:
            loop_start = time.time()

            txn = txn_gen.generate()

            if fraud_injector.should_inject():
                txn = fraud_injector.inject(txn)
                total_fraud += 1

            if producer:
                producer.send(txn)
            total_sent += 1

            # Rate limiting
            elapsed = time.time() - loop_start
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

            # Log progress every 1000 events
            if total_sent % 1000 == 0:
                runtime = time.time() - start_time
                actual_eps = total_sent / runtime if runtime > 0 else 0
                logger.info(
                    "Sent %d events (%d fraud, %.1f eps)",
                    total_sent,
                    total_fraud,
                    actual_eps,
                )

            # Check duration
            if args.duration > 0 and (time.time() - start_time) >= args.duration:
                break

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if producer:
            producer.flush()
            logger.info("Final stats: %s", producer.stats)

    runtime = time.time() - start_time
    logger.info(
        "Done: %d events in %.1fs (%.1f eps, %d fraud [%.1f%%])",
        total_sent,
        runtime,
        total_sent / runtime if runtime > 0 else 0,
        total_fraud,
        (total_fraud / total_sent * 100) if total_sent > 0 else 0,
    )


if __name__ == "__main__":
    main()
