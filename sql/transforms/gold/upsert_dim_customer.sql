-- Upsert dim_customer from silver.customers
INSERT INTO gold.dim_customer (customer_id, name, email, city, state, risk_profile, avg_transaction_amount, total_transactions, updated_at)
SELECT customer_id, name, email, city, state, risk_profile, avg_transaction_amount, total_transactions, NOW()
FROM silver.customers
WHERE updated_at > NOW() - INTERVAL '2 hours'
ON CONFLICT (customer_id)
DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    city = EXCLUDED.city,
    state = EXCLUDED.state,
    risk_profile = EXCLUDED.risk_profile,
    avg_transaction_amount = EXCLUDED.avg_transaction_amount,
    total_transactions = EXCLUDED.total_transactions,
    updated_at = NOW();
