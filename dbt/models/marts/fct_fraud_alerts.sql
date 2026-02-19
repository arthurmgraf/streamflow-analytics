{{
    config(
        materialized='incremental',
        unique_key='transaction_id'
    )
}}

with alerts as (
    select * from {{ ref('stg_fraud_alerts') }}
    {% if is_incremental() %}
    where detected_at > (
        select coalesce(max(loaded_at), '1970-01-01'::timestamptz)
        from {{ this }}
    )
    {% endif %}
),

customers as (
    select * from {{ ref('dim_customer') }}
)

select
    a.transaction_id,
    to_char(a.detected_at, 'YYYYMMDD')::integer as date_key,
    a.customer_id,
    a.alert_type,
    a.fraud_score,
    a.rules_triggered,
    a.detected_at,
    now() as loaded_at
from alerts a
inner join customers c on c.customer_id = a.customer_id
