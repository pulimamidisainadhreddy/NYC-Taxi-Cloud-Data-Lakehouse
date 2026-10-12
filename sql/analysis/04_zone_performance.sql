SELECT pickup_location_id, total_trips, total_revenue, average_fare, average_distance
FROM nyc_taxi.mart_zone_performance
ORDER BY total_revenue DESC
LIMIT 20;
