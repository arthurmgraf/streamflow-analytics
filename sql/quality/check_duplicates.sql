-- Check for duplicate transaction_ids in Silver layer
SELECT transaction_id, COUNT(*) AS dup_count
FROM silver.clean_transactions
WHERE processed_at > NOW() - INTERVAL '1 hour'
GROUP BY transaction_id
HAVING COUNT(*) > 1
LIMIT 10;
