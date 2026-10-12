from datetime import datetime

from pyspark.sql import SparkSession
from src.spark.transformations import (
    add_business_columns,
    deduplicate,
)


def make_spark() -> SparkSession:
    return SparkSession.builder.master("local[2]").appName("transform-test").getOrCreate()


def test_deduplicate() -> None:
    spark = make_spark()

    try:
        trip = (
            datetime(2025, 1, 1, 10, 0),
            datetime(2025, 1, 1, 10, 15),
            1,
            2,
            2.0,
            10.0,
        )

        df = spark.createDataFrame(
            [trip, trip],
            [
                "tpep_pickup_datetime",
                "tpep_dropoff_datetime",
                "PULocationID",
                "DOLocationID",
                "trip_distance",
                "total_amount",
            ],
        )

        assert deduplicate(df).count() == 1

    finally:
        spark.stop()


def test_revenue_per_mile() -> None:
    spark = make_spark()

    try:
        df = spark.createDataFrame(
            [(2.0, 10.0, 30.0)],
            [
                "trip_distance",
                "total_amount",
                "trip_duration_minutes",
            ],
        )

        result = add_business_columns(df).collect()

        assert result[0]["revenue_per_mile"] == 5.0

    finally:
        spark.stop()
