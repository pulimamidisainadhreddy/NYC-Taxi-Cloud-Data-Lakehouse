from __future__ import annotations
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def normalize_columns(df: DataFrame) -> DataFrame:
    """Normalize key TLC fields to stable analytical types."""
    return (
        df.withColumn("PULocationID", F.col("PULocationID").cast("integer"))
        .withColumn("DOLocationID", F.col("DOLocationID").cast("integer"))
        .withColumn("passenger_count", F.col("passenger_count").cast("double"))
        .withColumn("trip_distance", F.col("trip_distance").cast("double"))
        .withColumn("fare_amount", F.col("fare_amount").cast("double"))
        .withColumn("tip_amount", F.col("tip_amount").cast("double"))
        .withColumn("tolls_amount", F.col("tolls_amount").cast("double"))
        .withColumn("total_amount", F.col("total_amount").cast("double"))
        .withColumn("payment_type", F.col("payment_type").cast("integer"))
    )


def deduplicate(df: DataFrame) -> DataFrame:
    return df.dropDuplicates(
        [
            "tpep_pickup_datetime",
            "tpep_dropoff_datetime",
            "PULocationID",
            "DOLocationID",
            "trip_distance",
            "total_amount",
        ]
    )


def add_business_columns(df: DataFrame) -> DataFrame:
    return df.withColumn(
        "revenue_per_mile",
        F.when(F.col("trip_distance") > 0, F.col("total_amount") / F.col("trip_distance")),
    ).withColumn(
        "average_speed_mph",
        F.when(
            F.col("trip_duration_minutes") > 0,
            F.col("trip_distance") / (F.col("trip_duration_minutes") / 60.0),
        ),
    )
