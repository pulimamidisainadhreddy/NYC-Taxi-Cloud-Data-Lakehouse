{{ config(materialized='table') }}
select payment_type, count(*) as total_trips, sum(total_amount) as total_revenue,
       avg(total_amount) as average_fare
from {{ ref('fct_trips') }} group by 1
