-- Check data freshness: fail if no new data in last 30 minutes
SELECT
    'bronze.raw_transactions' AS table_name,
    MAX(ingested_at) AS latest_record,
    NOW() - MAX(ingested_at) AS staleness
FROM bronze.raw_transactions
HAVING NOW() - MAX(ingested_at) > INTERVAL '30 minutes';
