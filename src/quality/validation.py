from __future__ import annotations
from dataclasses import dataclass
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

REQUIRED_COLUMNS = {
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "PULocationID",
    "DOLocationID",
    "fare_amount",
    "tip_amount",
    "tolls_amount",
    "total_amount",
    "payment_type",
}


@dataclass
class QualityResult:
    name: str
    passed: bool
    failed_records: int


def check_required_columns(df: DataFrame) -> QualityResult:
    missing = REQUIRED_COLUMNS.difference(df.columns)
    return QualityResult("required_columns", not missing, len(missing))


def invalid_trip_condition():
    return (
        (F.col("tpep_dropoff_datetime") < F.col("tpep_pickup_datetime"))
        | (F.col("trip_distance") < 0)
        | (F.col("fare_amount") < 0)
        | (F.col("total_amount") < 0)
        | (F.col("passenger_count") < 0)
    )


def invalid_trip_conditions(df: DataFrame) -> DataFrame:
    return df.filter(invalid_trip_condition())


def add_quality_columns(df: DataFrame) -> DataFrame:
    return (
        df.withColumn(
            "trip_duration_minutes",
            (F.unix_timestamp("tpep_dropoff_datetime") - F.unix_timestamp("tpep_pickup_datetime"))
            / 60.0,
        )
        .withColumn("pickup_date", F.to_date("tpep_pickup_datetime"))
        .withColumn("pickup_hour", F.hour("tpep_pickup_datetime"))
    )
