-- Check null rate on critical Silver columns
-- Fails if null rate exceeds 5% on any critical field
SELECT
    'silver.clean_transactions' AS table_name,
    'customer_id' AS column_name,
    COUNT(*) FILTER (WHERE customer_id IS NULL)::FLOAT / NULLIF(COUNT(*), 0) AS null_rate
FROM silver.clean_transactions
WHERE processed_at > NOW() - INTERVAL '1 hour'
HAVING COUNT(*) FILTER (WHERE customer_id IS NULL)::FLOAT / NULLIF(COUNT(*), 0) > 0.05;
