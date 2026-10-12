{{ config(materialized='table') }}
select pickup_hour, count(*) as total_trips, sum(total_amount) as total_revenue,
       avg(trip_distance) as average_distance, avg(trip_duration_minutes) as average_duration
from {{ ref('fct_trips') }} group by 1 order by 1
