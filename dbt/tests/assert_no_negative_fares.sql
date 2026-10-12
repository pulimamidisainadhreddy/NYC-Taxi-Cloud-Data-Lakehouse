select * from {{ ref('fct_trips') }} where fare_amount < 0 or total_amount < 0
