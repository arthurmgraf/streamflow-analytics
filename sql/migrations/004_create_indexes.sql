-- StreamFlow Analytics: Additional performance indexes
-- Run after all schemas are created

-- Quality tracking table
CREATE TABLE IF NOT EXISTS silver.quality_check_results (
    id              BIGSERIAL PRIMARY KEY,
    check_name      VARCHAR(100) NOT NULL,
    table_name      VARCHAR(100) NOT NULL,
    status          VARCHAR(20) NOT NULL,  -- 'pass', 'fail', 'warn'
    metric_value    NUMERIC(12,4),
    threshold       NUMERIC(12,4),
    details         JSONB,
    checked_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_quality_checked ON silver.quality_check_results (checked_at);
CREATE INDEX idx_quality_status ON silver.quality_check_results (status) WHERE status != 'pass';

-- Populate dim_date for 2025-2027
INSERT INTO gold.dim_date (date_key, full_date, day_of_week, day_name, month, month_name, quarter, year, is_weekend)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER AS date_key,
    d::DATE AS full_date,
    EXTRACT(DOW FROM d)::SMALLINT AS day_of_week,
    TO_CHAR(d, 'Day') AS day_name,
    EXTRACT(MONTH FROM d)::SMALLINT AS month,
    TO_CHAR(d, 'Month') AS month_name,
    EXTRACT(QUARTER FROM d)::SMALLINT AS quarter,
    EXTRACT(YEAR FROM d)::SMALLINT AS year,
    EXTRACT(DOW FROM d) IN (0, 6) AS is_weekend
FROM generate_series('2025-01-01'::DATE, '2027-12-31'::DATE, '1 day'::INTERVAL) AS d
ON CONFLICT (date_key) DO NOTHING;
