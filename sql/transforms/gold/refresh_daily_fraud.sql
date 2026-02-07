-- Refresh daily fraud summary aggregate
INSERT INTO gold.agg_daily_fraud (day_bucket, total_alerts, avg_fraud_score, high_severity_count, unique_customers, refreshed_at)
SELECT
    date_trunc('day', f.detected_at) AS day_bucket,
    COUNT(*) AS total_alerts,
    AVG(f.fraud_score) AS avg_fraud_score,
    COUNT(*) FILTER (WHERE f.fraud_score > 0.9) AS high_severity_count,
    COUNT(DISTINCT f.customer_id) AS unique_customers,
    NOW()
FROM gold.fact_fraud_alerts f
WHERE f.detected_at > NOW() - INTERVAL '2 days'
GROUP BY date_trunc('day', f.detected_at)
ON CONFLICT (day_bucket)
DO UPDATE SET
    total_alerts = EXCLUDED.total_alerts,
    avg_fraud_score = EXCLUDED.avg_fraud_score,
    high_severity_count = EXCLUDED.high_severity_count,
    unique_customers = EXCLUDED.unique_customers,
    refreshed_at = NOW();
