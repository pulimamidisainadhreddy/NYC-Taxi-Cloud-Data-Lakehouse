{{ config(materialized='view') }}
{% if target.type == 'duckdb' %}
select
    cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
    cast(passenger_count as double) as passenger_count,
    cast(trip_distance as double) as trip_distance,
    cast(PULocationID as integer) as pickup_location_id,
    cast(DOLocationID as integer) as dropoff_location_id,
    cast(fare_amount as double) as fare_amount,
    cast(tip_amount as double) as tip_amount,
    cast(tolls_amount as double) as tolls_amount,
    cast(total_amount as double) as total_amount,
    cast(payment_type as integer) as payment_type,
    cast(pickup_date as date) as pickup_date,
    cast(pickup_hour as integer) as pickup_hour,
    cast(trip_duration_minutes as double) as trip_duration_minutes,
    cast(revenue_per_mile as double) as revenue_per_mile
from read_parquet('/opt/project/local-lake/silver/**/*.parquet', union_by_name=true)
{% else %}
select
    cast(tpep_pickup_datetime as timestamp) as pickup_datetime,
    cast(tpep_dropoff_datetime as timestamp) as dropoff_datetime,
    cast(passenger_count as double) as passenger_count,
    cast(trip_distance as double) as trip_distance,
    cast(PULocationID as integer) as pickup_location_id,
    cast(DOLocationID as integer) as dropoff_location_id,
    cast(fare_amount as double) as fare_amount,
    cast(tip_amount as double) as tip_amount,
    cast(tolls_amount as double) as tolls_amount,
    cast(total_amount as double) as total_amount,
    cast(payment_type as integer) as payment_type,
    cast(pickup_date as date) as pickup_date,
    cast(pickup_hour as integer) as pickup_hour,
    cast(trip_duration_minutes as double) as trip_duration_minutes,
    cast(revenue_per_mile as double) as revenue_per_mile
from {{ source('nyc_taxi', 'silver_yellow_taxi') }}
{% endif %}
