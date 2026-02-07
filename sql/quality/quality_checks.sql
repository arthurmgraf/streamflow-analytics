-- Data Quality Checks
-- Results logged to silver.quality_check_results

-- Check 1: Null rate in clean_transactions
INSERT INTO silver.quality_check_results (check_name, table_name, status, metric_value, threshold, details)
SELECT
    'null_rate_customer_id',
    'silver.clean_transactions',
    CASE WHEN null_rate < 0.05 THEN 'pass' ELSE 'fail' END,
    null_rate,
    0.05,
    jsonb_build_object('total_rows', total, 'null_rows', nulls)
FROM (
    SELECT
        COUNT(*) AS total,
        COUNT(*) FILTER (WHERE customer_id IS NULL) AS nulls,
        COUNT(*) FILTER (WHERE customer_id IS NULL)::NUMERIC / GREATEST(COUNT(*), 1) AS null_rate
    FROM silver.clean_transactions
    WHERE cleaned_at > NOW() - INTERVAL '1 hour'
) stats;

-- Check 2: Duplicate transaction_ids
INSERT INTO silver.quality_check_results (check_name, table_name, status, metric_value, threshold, details)
SELECT
    'duplicate_transaction_ids',
    'silver.clean_transactions',
    CASE WHEN dup_count = 0 THEN 'pass' ELSE 'fail' END,
    dup_count,
    0,
    jsonb_build_object('duplicate_count', dup_count)
FROM (
    SELECT COUNT(*) AS dup_count
    FROM (
        SELECT transaction_id
        FROM silver.clean_transactions
        GROUP BY transaction_id
        HAVING COUNT(*) > 1
    ) dups
) stats;

-- Check 3: Freshness (last record < 30 min old)
INSERT INTO silver.quality_check_results (check_name, table_name, status, metric_value, threshold, details)
SELECT
    'data_freshness_minutes',
    'silver.clean_transactions',
    CASE WHEN age_minutes < 30 THEN 'pass'
         WHEN age_minutes < 60 THEN 'warn'
         ELSE 'fail'
    END,
    age_minutes,
    30,
    jsonb_build_object('last_record_at', last_record, 'age_minutes', age_minutes)
FROM (
    SELECT
        MAX(cleaned_at) AS last_record,
        EXTRACT(EPOCH FROM NOW() - MAX(cleaned_at)) / 60 AS age_minutes
    FROM silver.clean_transactions
) stats;

-- Check 4: Amount range validity
INSERT INTO silver.quality_check_results (check_name, table_name, status, metric_value, threshold, details)
SELECT
    'invalid_amounts',
    'silver.clean_transactions',
    CASE WHEN invalid_count = 0 THEN 'pass' ELSE 'fail' END,
    invalid_count,
    0,
    jsonb_build_object('invalid_count', invalid_count, 'min_amount', min_amt, 'max_amount', max_amt)
FROM (
    SELECT
        COUNT(*) FILTER (WHERE amount <= 0 OR amount > 999999) AS invalid_count,
        MIN(amount) AS min_amt,
        MAX(amount) AS max_amt
    FROM silver.clean_transactions
    WHERE cleaned_at > NOW() - INTERVAL '1 hour'
) stats;
