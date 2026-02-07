"""Store data generator."""

from __future__ import annotations

import random
import uuid

from src.models.store import Store

# Brazilian cities with approximate coordinates
STORE_LOCATIONS = [
    ("São Paulo", "SP", -23.5505, -46.6333),
    ("Rio de Janeiro", "RJ", -22.9068, -43.1729),
    ("Belo Horizonte", "MG", -19.9167, -43.9345),
    ("Curitiba", "PR", -25.4284, -49.2733),
    ("Porto Alegre", "RS", -30.0346, -51.2177),
    ("Salvador", "BA", -12.9714, -38.5124),
    ("Brasília", "DF", -15.7975, -47.8919),
    ("Recife", "PE", -8.0476, -34.8770),
    ("Fortaleza", "CE", -3.7172, -38.5433),
    ("Manaus", "AM", -3.1190, -60.0217),
]

CATEGORIES = [
    "electronics", "clothing", "food", "pharmacy", "supermarket",
    "furniture", "sports", "books", "cosmetics", "automotive",
]

STORE_PREFIXES = [
    "Loja", "Casa", "Super", "Mega", "Center", "Ponto", "Mundo", "Top",
]


def generate_stores(count: int, seed: int | None = None) -> list[Store]:
    """Generate a list of realistic Brazilian stores.

    Args:
        count: Number of stores to generate.
        seed: Random seed for reproducibility.

    Returns:
        List of Store models.
    """
    rng = random.Random(seed)
    stores: list[Store] = []

    for _i in range(count):
        city, state, base_lat, base_lon = rng.choice(STORE_LOCATIONS)
        category = rng.choice(CATEGORIES)
        prefix = rng.choice(STORE_PREFIXES)

        # Add small offset for variety
        lat = base_lat + rng.uniform(-0.05, 0.05)
        lon = base_lon + rng.uniform(-0.05, 0.05)

        store = Store(
            store_id=f"store-{uuid.UUID(int=rng.getrandbits(128)).hex[:8]}",
            name=f"{prefix} {category.title()} {city}",
            city=city,
            state=state,
            latitude=round(lat, 6),
            longitude=round(lon, 6),
            category=category,
        )
        stores.append(store)

    return stores
