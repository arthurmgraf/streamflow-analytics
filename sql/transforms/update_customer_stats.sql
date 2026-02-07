-- Update customer aggregate statistics in Silver layer
-- Run after bronze_to_silver transform

INSERT INTO silver.customers (customer_id, name, avg_transaction_amt, total_transactions, updated_at)
SELECT
    customer_id,
    COALESCE(MAX(raw_payload->>'customer_name'), 'Unknown') AS name,
    AVG((raw_payload->>'amount')::NUMERIC(12,2))            AS avg_transaction_amt,
    COUNT(*)                                                AS total_transactions,
    NOW()                                                   AS updated_at
FROM bronze.raw_transactions
GROUP BY customer_id
ON CONFLICT (customer_id) DO UPDATE SET
    avg_transaction_amt = EXCLUDED.avg_transaction_amt,
    total_transactions = EXCLUDED.total_transactions,
    updated_at = NOW();
