-- Load new fraud alerts into fact_fraud_alerts
INSERT INTO gold.fact_fraud_alerts (transaction_id, customer_id, fraud_score, rules_triggered, alert_type, detected_at, loaded_at)
SELECT a.transaction_id, a.customer_id, a.fraud_score, a.rules_triggered, a.alert_type, a.detected_at, NOW()
FROM silver.fraud_alerts a
LEFT JOIN gold.fact_fraud_alerts f ON a.transaction_id = f.transaction_id
WHERE f.transaction_id IS NULL
  AND a.processed_at > NOW() - INTERVAL '2 hours';
