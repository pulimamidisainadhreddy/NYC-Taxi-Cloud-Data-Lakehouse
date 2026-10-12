{{ config(materialized='table') }}
select pickup_location_id, count(*) as total_trips, sum(total_amount) as total_revenue,
       avg(total_amount) as average_fare, avg(trip_distance) as average_distance
from {{ ref('fct_trips') }} group by 1
