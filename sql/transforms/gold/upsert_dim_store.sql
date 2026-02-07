-- Upsert dim_store from silver.stores
INSERT INTO gold.dim_store (store_id, name, city, state, latitude, longitude, category, updated_at)
SELECT store_id, name, city, state, latitude, longitude, category, NOW()
FROM silver.stores
WHERE updated_at > NOW() - INTERVAL '2 hours'
ON CONFLICT (store_id)
DO UPDATE SET
    name = EXCLUDED.name,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    category = EXCLUDED.category,
    updated_at = NOW();
