with transactions as (
    select * from {{ ref('stg_transactions') }}
    where is_valid = true
),

stats as (
    select
        customer_id,
        coalesce(max(
            (select s.raw_payload->>'customer_name'
             from {{ source('bronze', 'raw_transactions') }} s
             where s.raw_payload->>'customer_id' = transactions.customer_id
             limit 1)
        ), 'Unknown') as name,
        avg(amount) as avg_transaction_amt,
        count(*) as total_transactions,
        min(transaction_at) as first_seen_at,
        max(transaction_at) as last_seen_at,
        count(*) filter (where is_fraud) as fraud_count,
        case
            when count(*) filter (where is_fraud)::numeric / nullif(count(*), 0) > 0.1
                then 'high'
            when count(*) filter (where is_fraud)::numeric / nullif(count(*), 0) > 0.05
                then 'medium'
            else 'normal'
        end as risk_profile,
        now() as updated_at
    from transactions
    group by customer_id
)

select * from stats
