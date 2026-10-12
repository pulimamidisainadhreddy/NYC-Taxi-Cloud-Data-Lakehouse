from datetime import datetime

from pyspark.sql import SparkSession
from src.quality.validation import invalid_trip_conditions


def test_invalid_trip_is_detected() -> None:
    spark = SparkSession.builder.master("local[2]").appName("quality-test").getOrCreate()

    try:
        df = spark.createDataFrame(
            [
                (
                    datetime(2025, 1, 1, 10, 0),
                    datetime(2025, 1, 1, 10, 10),
                    10.0,
                    -1.0,
                    5.0,
                    10.0,
                )
            ],
            [
                "tpep_pickup_datetime",
                "tpep_dropoff_datetime",
                "trip_distance",
                "fare_amount",
                "passenger_count",
                "total_amount",
            ],
        )

        assert invalid_trip_conditions(df).count() == 1

    finally:
        spark.stop()
