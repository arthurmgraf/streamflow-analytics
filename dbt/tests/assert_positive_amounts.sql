-- Singular test: ensure all transaction amounts are positive
-- Returns rows that fail (dbt convention: test fails if query returns rows)

select
    transaction_id,
    amount
from {{ ref('stg_transactions') }}
where amount <= 0
