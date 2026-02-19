{{
    config(
        materialized='incremental',
        unique_key='date_key'
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
),

alerts as (
    select * from {{ ref('fct_fraud_alerts') }}
),

daily as (
    select
        f.date_key,
        count(distinct case when a.transaction_id is not null then a.transaction_id end) as total_alerts,
        count(distinct f.transaction_id) as total_txns,
        case
            when count(distinct f.transaction_id) > 0
            then count(distinct case when a.transaction_id is not null then a.transaction_id end)::numeric
                 / count(distinct f.transaction_id)
            else 0
        end as fraud_rate,
        mode() within group (order by a.alert_type) as top_rule,
        avg(a.fraud_score) as avg_score,
        now() as computed_at
    from facts f
    left join alerts a on a.date_key = f.date_key
    group by f.date_key
)

select * from daily
