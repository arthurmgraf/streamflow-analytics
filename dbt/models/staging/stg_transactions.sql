{{
    config(
        materialized='incremental',
        unique_key='transaction_id',
        on_schema_change='append_new_columns'
    )
}}

with source as (
    select * from {{ source('bronze', 'raw_transactions') }}
    {% if is_incremental() %}
    where ingested_at > (
        select coalesce(max(cleaned_at), '1970-01-01'::timestamptz)
        from {{ this }}
    )
    {% endif %}
),

fraud_scores as (
    select
        transaction_id,
        max(fraud_score) as max_score
    from {{ source('bronze', 'raw_fraud_alerts') }}
    group by transaction_id
),

cleaned as (
    select
        s.raw_payload->>'transaction_id'              as transaction_id,
        s.raw_payload->>'customer_id'                 as customer_id,
        s.raw_payload->>'store_id'                    as store_id,
        s.raw_payload->>'product_id'                  as product_id,
        (s.raw_payload->>'amount')::numeric(12,2)     as amount,
        coalesce(s.raw_payload->>'currency', 'BRL')   as currency,
        s.raw_payload->>'payment_method'              as payment_method,
        (s.raw_payload->>'timestamp')::timestamptz    as transaction_at,
        (s.raw_payload->>'latitude')::numeric(9,6)    as latitude,
        (s.raw_payload->>'longitude')::numeric(9,6)   as longitude,
        coalesce(f.max_score, 0.0)                    as fraud_score,
        coalesce(f.max_score, 0.0) > 0.7              as is_fraud,
        (s.raw_payload->>'transaction_id') is not null
            and (s.raw_payload->>'amount')::numeric > 0
                                                      as is_valid,
        jsonb_build_object(
            'has_location', (s.raw_payload->>'latitude') is not null,
            'has_product', (s.raw_payload->>'product_id') is not null
        )                                             as quality_checks,
        now()                                         as cleaned_at
    from source s
    left join fraud_scores f
        on f.transaction_id = s.raw_payload->>'transaction_id'
)

select * from cleaned
