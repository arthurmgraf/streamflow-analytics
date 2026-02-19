with customer_stats as (
    select * from {{ ref('int_customer_stats') }}
)

select
    customer_id,
    name,
    risk_profile,
    avg_transaction_amt,
    total_transactions,
    first_seen_at,
    now() as valid_from
from customer_stats
