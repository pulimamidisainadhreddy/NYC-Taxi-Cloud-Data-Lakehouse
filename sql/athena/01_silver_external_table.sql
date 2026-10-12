-- Replace REPLACE_ME with your private S3 bucket.
CREATE EXTERNAL TABLE IF NOT EXISTS nyc_taxi.silver_yellow_taxi (
  tpep_pickup_datetime timestamp,
  tpep_dropoff_datetime timestamp,
  passenger_count double,
  trip_distance double,
  PULocationID int,
  DOLocationID int,
  fare_amount double,
  tip_amount double,
  tolls_amount double,
  total_amount double,
  payment_type int,
  pickup_date date,
  pickup_hour int,
  trip_duration_minutes double,
  revenue_per_mile double,
  average_speed_mph double
)
STORED AS PARQUET
LOCATION 's3://REPLACE_ME/silver/yellow_taxi/';
