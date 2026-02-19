{{
    config(
        materialized='incremental',
        unique_key='transaction_id'
    )
}}

with transactions as (
    select * from {{ ref('stg_transactions') }}
    where is_valid = true
    {% if is_incremental() %}
    and cleaned_at > (
        select coalesce(max(loaded_at), '1970-01-01'::timestamptz)
        from {{ this }}
    )
    {% endif %}
),

customers as (
    select * from {{ ref('dim_customer') }}
),

stores as (
    select * from {{ ref('dim_store') }}
)

select
    t.transaction_id,
    to_char(t.transaction_at, 'YYYYMMDD')::integer as date_key,
    t.customer_id,
    t.store_id,
    t.product_id,
    t.amount,
    t.currency,
    t.payment_method,
    t.fraud_score,
    t.is_fraud,
    t.transaction_at,
    now() as loaded_at
from transactions t
inner join customers c on c.customer_id = t.customer_id
inner join stores s on s.store_id = t.store_id
