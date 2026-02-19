{{
    config(
        materialized='incremental',
        unique_key=['hour_timestamp', 'store_id']
    )
}}

with facts as (
    select * from {{ ref('fct_transactions') }}
    {% if is_incremental() %}
    where loaded_at > (
        select coalesce(max(computed_at), '1970-01-01'::timestamptz)
        from {{ this }}
    )
    {% endif %}
)

select
    date_trunc('hour', transaction_at) as hour_timestamp,
    store_id,
    count(*) as transaction_count,
    sum(amount) as total_amount,
    avg(amount) as avg_amount,
    count(*) filter (where is_fraud) as fraud_count,
    now() as computed_at
from facts
group by date_trunc('hour', transaction_at), store_id
