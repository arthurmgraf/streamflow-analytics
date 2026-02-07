-- Bronze → Silver: Transform raw transactions to clean format
-- Incremental: processes rows not yet in silver (based on ingested_at watermark)

INSERT INTO silver.clean_transactions (
    transaction_id,
    customer_id,
    store_id,
    product_id,
    amount,
    currency,
    payment_method,
    transaction_at,
    latitude,
    longitude,
    fraud_score,
    is_fraud,
    is_valid,
    quality_checks,
    cleaned_at
)
SELECT
    raw_payload->>'transaction_id'                      AS transaction_id,
    raw_payload->>'customer_id'                         AS customer_id,
    raw_payload->>'store_id'                            AS store_id,
    raw_payload->>'product_id'                          AS product_id,
    (raw_payload->>'amount')::NUMERIC(12,2)             AS amount,
    COALESCE(raw_payload->>'currency', 'BRL')           AS currency,
    raw_payload->>'payment_method'                      AS payment_method,
    (raw_payload->>'timestamp')::TIMESTAMPTZ            AS transaction_at,
    (raw_payload->>'latitude')::NUMERIC(9,6)            AS latitude,
    (raw_payload->>'longitude')::NUMERIC(9,6)           AS longitude,
    COALESCE(fa.max_score, 0.0)                         AS fraud_score,
    COALESCE(fa.max_score, 0.0) > 0.7                   AS is_fraud,
    -- Validity checks
    (raw_payload->>'transaction_id') IS NOT NULL
        AND (raw_payload->>'amount')::NUMERIC > 0       AS is_valid,
    jsonb_build_object(
        'has_location', (raw_payload->>'latitude') IS NOT NULL,
        'has_product', (raw_payload->>'product_id') IS NOT NULL
    )                                                   AS quality_checks,
    NOW()                                               AS cleaned_at
FROM bronze.raw_transactions rt
LEFT JOIN LATERAL (
    SELECT MAX(fraud_score) AS max_score
    FROM bronze.raw_fraud_alerts fa
    WHERE fa.transaction_id = rt.raw_payload->>'transaction_id'
) fa ON TRUE
WHERE rt.ingested_at > COALESCE(
    (SELECT MAX(cleaned_at) FROM silver.clean_transactions),
    '1970-01-01'::TIMESTAMPTZ
)
ON CONFLICT (transaction_id) DO UPDATE SET
    fraud_score = EXCLUDED.fraud_score,
    is_fraud = EXCLUDED.is_fraud,
    cleaned_at = NOW();
