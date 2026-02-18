"""Realistic transaction event generator."""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

from src.models.customer import Customer
from src.models.store import Store
from src.models.transaction import Transaction

PAYMENT_METHODS = ["credit_card", "debit_card", "pix", "boleto"]
PRODUCT_CATEGORIES = {
    "electronics": (50.0, 5000.0),
    "clothing": (30.0, 800.0),
    "food": (5.0, 200.0),
    "pharmacy": (10.0, 500.0),
    "supermarket": (20.0, 1500.0),
    "furniture": (100.0, 10000.0),
    "sports": (30.0, 3000.0),
    "books": (10.0, 300.0),
    "cosmetics": (15.0, 600.0),
    "automotive": (50.0, 8000.0),
}


class TransactionGenerator:
    """Generates realistic e-commerce transaction events.

    Maintains customer profiles for statistically plausible patterns.
    """

    def __init__(
        self,
        customers: list[Customer],
        stores: list[Store],
        seed: int | None = None,
    ) -> None:
        self.customers = customers
        self.stores = stores
        self.rng = random.Random(seed)
        self._customer_patterns: dict[str, dict[str, Any]] = {}

        # Build per-customer spending patterns
        for customer in customers:
            self._customer_patterns[customer.customer_id] = {
                "avg_amount": self.rng.uniform(50, 500),
                "std_amount": self.rng.uniform(20, 200),
                "preferred_hours": self.rng.sample(range(8, 23), k=5),
                "preferred_stores": self.rng.sample(stores, k=min(3, len(stores))),
                "preferred_payment": self.rng.choice(PAYMENT_METHODS),
            }

    def generate(self, timestamp: datetime | None = None) -> Transaction:
        """Generate a single realistic transaction.

        Args:
            timestamp: Transaction time. Defaults to now.

        Returns:
            A validated Transaction model.
        """
        customer = self.rng.choice(self.customers)
        pattern = self._customer_patterns[customer.customer_id]

        # Prefer familiar stores (80%) vs random (20%)
        if self.rng.random() < 0.8:
            store = self.rng.choice(pattern["preferred_stores"])
        else:
            store = self.rng.choice(self.stores)

        # Amount based on store category + customer pattern
        category = store.category or "supermarket"
        min_amt, max_amt = PRODUCT_CATEGORIES.get(category, (10.0, 1000.0))
        base_amount = self.rng.gauss(pattern["avg_amount"], pattern["std_amount"])
        amount = max(min_amt, min(max_amt, abs(base_amount)))

        if timestamp is None:
            timestamp = datetime.now()

        # Use store location with small jitter
        lat = None
        lon = None
        if store.latitude is not None and store.longitude is not None:
            lat = store.latitude + self.rng.uniform(-0.01, 0.01)
            lon = store.longitude + self.rng.uniform(-0.01, 0.01)

        return Transaction(
            transaction_id=f"txn-{uuid.uuid4().hex[:16]}",
            customer_id=customer.customer_id,
            store_id=store.store_id,
            product_id=f"prod-{self.rng.randint(1, 50):04d}",
            amount=Decimal(str(round(amount, 2))),
            currency="BRL",
            payment_method=(
                pattern["preferred_payment"]
                if self.rng.random() < 0.7
                else self.rng.choice(PAYMENT_METHODS)
            ),
            latitude=lat,
            longitude=lon,
            timestamp=timestamp,
        )

    def generate_batch(
        self,
        count: int,
        start_time: datetime | None = None,
        interval_seconds: float = 1.0,
    ) -> list[Transaction]:
        """Generate a batch of transactions with incremental timestamps.

        Args:
            count: Number of transactions.
            start_time: First transaction time.
            interval_seconds: Average seconds between transactions.

        Returns:
            List of Transaction models.
        """
        if start_time is None:
            start_time = datetime.now()

        transactions: list[Transaction] = []
        current_time = start_time

        for _ in range(count):
            txn = self.generate(timestamp=current_time)
            transactions.append(txn)
            # Add jittered interval
            jitter = self.rng.uniform(0.1, interval_seconds * 2)
            current_time += timedelta(seconds=jitter)

        return transactions
