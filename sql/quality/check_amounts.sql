-- Check for suspicious amounts (negative, zero, or extremely high)
SELECT transaction_id, amount, 'SUSPICIOUS_AMOUNT' AS check_type
FROM silver.clean_transactions
WHERE cleaned_at > NOW() - INTERVAL '1 hour'
  AND (amount <= 0 OR amount > 1000000)
LIMIT 100;
