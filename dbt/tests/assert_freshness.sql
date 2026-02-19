-- Singular test: ensure staging data is less than 2 hours old
-- Returns a row if data is stale (dbt fails if query returns rows)

select
    max(cleaned_at) as last_cleaned,
    extract(epoch from now() - max(cleaned_at)) / 3600 as hours_since_last
from {{ ref('stg_transactions') }}
having extract(epoch from now() - max(cleaned_at)) / 3600 > 2
