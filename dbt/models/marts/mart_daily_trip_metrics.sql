{{ config(materialized='table') }}
select pickup_date, count(*) as total_trips, sum(total_amount) as total_revenue,
       avg(total_amount) as average_fare, avg(trip_distance) as average_trip_distance,
       avg(trip_duration_minutes) as average_trip_duration
from {{ ref('fct_trips') }} group by 1 order by 1
