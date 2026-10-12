{{ config(materialized='table') }}
select pickup_date, pickup_hour, pickup_location_id, dropoff_location_id,
       count(*) as trip_count, sum(total_amount) as total_revenue,
       avg(total_amount) as average_fare, avg(trip_distance) as average_distance,
       avg(trip_duration_minutes) as average_duration
from {{ ref('stg_yellow_taxi') }}
group by 1,2,3,4
