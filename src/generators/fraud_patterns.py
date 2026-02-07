"""Fraud pattern injection for synthetic data generation.

Modifies legitimate transactions to inject known fraud patterns,
matching the 5 detection rules (FR-001 through FR-005).
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

from src.models.customer import Customer
from src.models.store import Store
from src.models.transaction import Transaction


class FraudInjector:
    """Injects fraud patterns into transaction streams."""

    def __init__(
        self,
        customers: list[Customer],
        stores: list[Store],
        fraud_rate: float = 0.02,
        seed: int | None = None,
    ) -> None:
        self.customers = customers
        self.stores = stores
        self.fraud_rate = fraud_rate
        self.rng = random.Random(seed)

    def should_inject(self) -> bool:
        """Decide whether to inject a fraud pattern."""
        return self.rng.random() < self.fraud_rate

    def inject(self, base_txn: Transaction) -> Transaction:
        """Inject a random fraud pattern into a transaction.

        Args:
            base_txn: Original transaction to modify.

        Returns:
            Modified transaction with fraud characteristics.
        """
        pattern = self.rng.choice([
            self._inject_high_value,
            self._inject_velocity_burst,
            self._inject_geographic_anomaly,
            self._inject_time_anomaly,
        ])
        return pattern(base_txn)

    def _inject_high_value(self, txn: Transaction) -> Transaction:
        """FR-001: Multiply amount by 5-20x."""
        multiplier = self.rng.uniform(5.0, 20.0)
        new_amount = Decimal(str(round(float(txn.amount) * multiplier, 2)))
        return txn.model_copy(update={"amount": new_amount})

    def _inject_velocity_burst(self, txn: Transaction) -> Transaction:
        """FR-002: Keep amount same but mark for burst generation.

        The actual burst (multiple txns in short time) is handled
        by generate_fraud_burst().
        """
        # Slightly higher amount for velocity fraud
        new_amount = Decimal(str(round(float(txn.amount) * 1.5, 2)))
        return txn.model_copy(update={"amount": new_amount})

    def _inject_geographic_anomaly(self, txn: Transaction) -> Transaction:
        """FR-003: Move transaction to a distant location."""
        # Pick a store far from original
        distant_store = self.rng.choice(self.stores)
        return txn.model_copy(update={
            "store_id": distant_store.store_id,
            "latitude": distant_store.latitude,
            "longitude": distant_store.longitude,
        })

    def _inject_time_anomaly(self, txn: Transaction) -> Transaction:
        """FR-004: Shift to unusual hours (2-5 AM)."""
        unusual_hour = self.rng.randint(2, 5)
        new_ts = txn.timestamp.replace(hour=unusual_hour, minute=self.rng.randint(0, 59))
        return txn.model_copy(update={"timestamp": new_ts})

    def generate_fraud_burst(
        self,
        customer_id: str,
        count: int = 8,
        window_seconds: int = 120,
    ) -> list[Transaction]:
        """Generate a velocity fraud burst: many transactions in short time.

        Args:
            customer_id: Target customer.
            count: Number of rapid transactions.
            window_seconds: Time window for burst.

        Returns:
            List of burst transactions.
        """
        store = self.rng.choice(self.stores)
        base_time = datetime.now()
        transactions: list[Transaction] = []

        for _i in range(count):
            offset = self.rng.uniform(0, window_seconds)
            txn = Transaction(
                transaction_id=f"txn-fraud-{uuid.uuid4().hex[:12]}",
                customer_id=customer_id,
                store_id=store.store_id,
                product_id=None,
                amount=Decimal(str(round(self.rng.uniform(50, 500), 2))),
                currency="BRL",
                payment_method="credit_card",
                latitude=store.latitude,
                longitude=store.longitude,
                timestamp=base_time + timedelta(seconds=offset),
            )
            transactions.append(txn)

        return sorted(transactions, key=lambda t: t.timestamp)
