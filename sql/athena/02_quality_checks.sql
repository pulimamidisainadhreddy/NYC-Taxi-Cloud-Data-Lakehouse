SELECT COUNT(*) AS invalid_duration_rows
FROM nyc_taxi.silver_yellow_taxi
WHERE trip_duration_minutes < 0;

SELECT COUNT(*) AS invalid_distance_rows
FROM nyc_taxi.silver_yellow_taxi
WHERE trip_distance < 0;
