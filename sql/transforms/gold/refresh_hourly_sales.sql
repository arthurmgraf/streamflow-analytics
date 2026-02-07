-- Refresh hourly sales aggregate
INSERT INTO gold.agg_hourly_sales (hour_bucket, store_id, total_amount, transaction_count, avg_amount, refreshed_at)
SELECT
    date_trunc('hour', t.transaction_timestamp) AS hour_bucket,
    t.store_id,
    SUM(t.amount) AS total_amount,
    COUNT(*) AS transaction_count,
    AVG(t.amount) AS avg_amount,
    NOW()
FROM gold.fact_transactions t
WHERE t.transaction_timestamp > NOW() - INTERVAL '3 hours'
GROUP BY date_trunc('hour', t.transaction_timestamp), t.store_id
ON CONFLICT (hour_bucket, store_id)
DO UPDATE SET
    total_amount = EXCLUDED.total_amount,
    transaction_count = EXCLUDED.transaction_count,
    avg_amount = EXCLUDED.avg_amount,
    refreshed_at = NOW();
