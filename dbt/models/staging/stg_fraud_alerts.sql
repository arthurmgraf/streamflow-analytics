{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        on_schema_change='append_new_columns'
    )
}}

with source as (
    select * from {{ source('bronze', 'raw_fraud_alerts') }}
    {% if is_incremental() %}
    where detected_at > (
        select coalesce(max(detected_at), '1970-01-01'::timestamptz)
        from {{ this }}
    )
    {% endif %}
),

cleaned as (
    select
        transaction_id,
        customer_id,
        alert_type,
        fraud_score,
        rules_triggered,
        raw_payload,
        detected_at,
        schema_version
    from source
)

select * from cleaned
