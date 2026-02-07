-- Load new transactions into fact_transactions
INSERT INTO gold.fact_transactions (transaction_id, customer_id, store_id, amount, currency, payment_method, latitude, longitude, transaction_timestamp, loaded_at)
SELECT t.transaction_id, t.customer_id, t.store_id, t.amount, t.currency, t.payment_method, t.latitude, t.longitude, t.timestamp, NOW()
FROM silver.clean_transactions t
LEFT JOIN gold.fact_transactions f ON t.transaction_id = f.transaction_id
WHERE f.transaction_id IS NULL
  AND t.processed_at > NOW() - INTERVAL '2 hours';
