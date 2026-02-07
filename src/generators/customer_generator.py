"""Customer profile generator."""

from __future__ import annotations

import random
import uuid

from src.models.customer import Customer, RiskProfile

# Brazilian cities with state codes
CITIES = [
    ("São Paulo", "SP"),
    ("Rio de Janeiro", "RJ"),
    ("Belo Horizonte", "MG"),
    ("Curitiba", "PR"),
    ("Porto Alegre", "RS"),
    ("Salvador", "BA"),
    ("Brasília", "DF"),
    ("Recife", "PE"),
    ("Fortaleza", "CE"),
    ("Manaus", "AM"),
]

FIRST_NAMES = [
    "Maria", "João", "Ana", "Pedro", "Juliana", "Carlos", "Fernanda",
    "Lucas", "Beatriz", "Rafael", "Camila", "Gabriel", "Larissa", "Mateus",
    "Amanda", "Bruno", "Letícia", "Diego", "Isabela", "Thiago",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Costa",
    "Rodrigues", "Almeida", "Nascimento", "Ferreira", "Araújo", "Carvalho",
    "Ribeiro", "Gomes", "Martins", "Barbosa", "Melo", "Rocha", "Dias",
]


def generate_customers(count: int, seed: int | None = None) -> list[Customer]:
    """Generate a list of realistic Brazilian customer profiles.

    Args:
        count: Number of customers to generate.
        seed: Random seed for reproducibility.

    Returns:
        List of Customer models.
    """
    rng = random.Random(seed)
    customers: list[Customer] = []

    for i in range(count):
        city, state = rng.choice(CITIES)
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)

        # 2% critical, 8% high, 70% normal, 20% low
        roll = rng.random()
        if roll < 0.02:
            risk = RiskProfile.CRITICAL
        elif roll < 0.10:
            risk = RiskProfile.HIGH
        elif roll < 0.80:
            risk = RiskProfile.NORMAL
        else:
            risk = RiskProfile.LOW

        customer = Customer(
            customer_id=f"cust-{uuid.UUID(int=rng.getrandbits(128)).hex[:12]}",
            name=f"{first} {last}",
            email=f"{first.lower()}.{last.lower()}{i}@email.com",
            city=city,
            state=state,
            risk_profile=risk,
        )
        customers.append(customer)

    return customers
