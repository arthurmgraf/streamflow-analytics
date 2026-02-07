-- Silver → Gold: Build dimensional model from clean data

-- 1. Upsert dim_customer
INSERT INTO gold.dim_customer (customer_id, name, city, state, risk_profile)
SELECT customer_id, name, city, state, risk_profile
FROM silver.customers
ON CONFLICT (customer_id) DO UPDATE SET
    name = EXCLUDED.name,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    risk_profile = EXCLUDED.risk_profile,
    valid_from = NOW();

-- 2. Upsert dim_store
INSERT INTO gold.dim_store (store_id, name, city, state, category)
SELECT store_id, name, city, state, category
FROM silver.stores
ON CONFLICT (store_id) DO UPDATE SET
    name = EXCLUDED.name,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    category = EXCLUDED.category;

-- 3. Upsert dim_product
INSERT INTO gold.dim_product (product_id, name, category, price)
SELECT product_id, name, category, price
FROM silver.products
ON CONFLICT (product_id) DO UPDATE SET
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    price = EXCLUDED.price;

-- 4. Load fact_transactions (incremental)
INSERT INTO gold.fact_transactions (
    transaction_id, date_key, customer_key, store_key, product_key,
    amount, fraud_score, is_fraud, transaction_at
)
SELECT
    ct.transaction_id,
    TO_CHAR(ct.transaction_at, 'YYYYMMDD')::INTEGER     AS date_key,
    dc.customer_key,
    ds.store_key,
    dp.product_key,
    ct.amount,
    ct.fraud_score,
    ct.is_fraud,
    ct.transaction_at
FROM silver.clean_transactions ct
JOIN gold.dim_customer dc ON dc.customer_id = ct.customer_id
JOIN gold.dim_store ds ON ds.store_id = ct.store_id
LEFT JOIN gold.dim_product dp ON dp.product_id = ct.product_id
WHERE ct.is_valid = TRUE
  AND ct.cleaned_at > COALESCE(
      (SELECT MAX(loaded_at) FROM gold.fact_transactions),
      '1970-01-01'::TIMESTAMPTZ
  )
ON CONFLICT (transaction_id) DO NOTHING;

-- 5. Load fact_fraud_alerts (incremental)
INSERT INTO gold.fact_fraud_alerts (
    date_key, customer_key, transaction_id, alert_type,
    fraud_score, rules_triggered, detected_at
)
SELECT
    TO_CHAR(fa.detected_at, 'YYYYMMDD')::INTEGER    AS date_key,
    dc.customer_key,
    fa.transaction_id,
    fa.alert_type,
    fa.fraud_score,
    ARRAY(SELECT jsonb_array_elements_text(fa.rules_triggered)) AS rules_triggered,
    fa.detected_at
FROM bronze.raw_fraud_alerts fa
JOIN gold.dim_customer dc ON dc.customer_id = fa.customer_id
WHERE fa.detected_at > COALESCE(
    (SELECT MAX(loaded_at) FROM gold.fact_fraud_alerts),
    '1970-01-01'::TIMESTAMPTZ
)
ON CONFLICT DO NOTHING;

-- 6. Refresh agg_hourly_sales
INSERT INTO gold.agg_hourly_sales (
    hour_timestamp, store_key, transaction_count,
    total_amount, avg_amount, fraud_count
)
SELECT
    DATE_TRUNC('hour', ft.transaction_at) AS hour_timestamp,
    ft.store_key,
    COUNT(*)                              AS transaction_count,
    SUM(ft.amount)                        AS total_amount,
    AVG(ft.amount)                        AS avg_amount,
    COUNT(*) FILTER (WHERE ft.is_fraud)   AS fraud_count
FROM gold.fact_transactions ft
WHERE ft.loaded_at > COALESCE(
    (SELECT MAX(computed_at) FROM gold.agg_hourly_sales),
    '1970-01-01'::TIMESTAMPTZ
)
GROUP BY DATE_TRUNC('hour', ft.transaction_at), ft.store_key
ON CONFLICT (hour_timestamp, store_key) DO UPDATE SET
    transaction_count = EXCLUDED.transaction_count,
    total_amount = EXCLUDED.total_amount,
    avg_amount = EXCLUDED.avg_amount,
    fraud_count = EXCLUDED.fraud_count,
    computed_at = NOW();

-- 7. Refresh agg_daily_fraud
INSERT INTO gold.agg_daily_fraud (
    date_key, total_alerts, total_txns, fraud_rate, top_rule, avg_score
)
SELECT
    ft.date_key,
    COUNT(DISTINCT ffa.alert_key)                     AS total_alerts,
    COUNT(DISTINCT ft.transaction_key)                AS total_txns,
    CASE WHEN COUNT(DISTINCT ft.transaction_key) > 0
         THEN COUNT(DISTINCT ffa.alert_key)::NUMERIC / COUNT(DISTINCT ft.transaction_key)
         ELSE 0
    END                                               AS fraud_rate,
    MODE() WITHIN GROUP (ORDER BY ffa.alert_type)     AS top_rule,
    AVG(ffa.fraud_score)                              AS avg_score
FROM gold.fact_transactions ft
LEFT JOIN gold.fact_fraud_alerts ffa ON ffa.date_key = ft.date_key
WHERE ft.loaded_at > COALESCE(
    (SELECT MAX(computed_at) FROM gold.agg_daily_fraud),
    '1970-01-01'::TIMESTAMPTZ
)
GROUP BY ft.date_key
ON CONFLICT (date_key) DO UPDATE SET
    total_alerts = EXCLUDED.total_alerts,
    total_txns = EXCLUDED.total_txns,
    fraud_rate = EXCLUDED.fraud_rate,
    top_rule = EXCLUDED.top_rule,
    avg_score = EXCLUDED.avg_score,
    computed_at = NOW();
