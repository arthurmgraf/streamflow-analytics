with stores as (
    select distinct
        store_id,
        first_value(latitude) over (partition by store_id order by transaction_at desc) as latitude,
        first_value(longitude) over (partition by store_id order by transaction_at desc) as longitude
    from {{ ref('stg_transactions') }}
    where store_id is not null
)

select
    store_id,
    latitude,
    longitude
from stores
