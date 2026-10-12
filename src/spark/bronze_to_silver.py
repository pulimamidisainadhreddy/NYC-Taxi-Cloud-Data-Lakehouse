from __future__ import annotations

import argparse
import logging
import time
import json

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.quality.validation import (
    add_quality_columns,
    check_required_columns,
    invalid_trip_condition,
)

from src.spark.transformations import (
    add_business_columns,
    deduplicate,
    normalize_columns,
)

from src.utils.logging_config import configure_logging

LOGGER = logging.getLogger(__name__)


def build_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("nyc-taxi-bronze-to-silver")
        .config("spark.sql.shuffle.partitions", "8")
        .config(
            "spark.hadoop.fs.s3a.impl",
            "org.apache.hadoop.fs.s3a.S3AFileSystem",
        )
        .config(
            "spark.hadoop.fs.s3a.endpoint",
            "s3.eu-central-1.amazonaws.com",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "com.amazonaws.auth.profile.ProfileCredentialsProvider",
        )
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider.profile.path",
            "/root/.aws/credentials",
        )
        .getOrCreate()
    )


def run(
    input_path: str,
    output_path: str,
    rejected_path: str | None = None,
) -> dict:

    start_time = time.perf_counter()
    spark = None

    LOGGER.info("pipeline_status=STARTED")
    LOGGER.info("input_path=%s", input_path)
    LOGGER.info("output_path=%s", output_path)

    try:
        spark = build_spark()

        # Step 1: Read Bronze data
        LOGGER.info("Reading Bronze data")

        df = spark.read.parquet(input_path)

        # Step 2: Check required columns
        required = check_required_columns(df)

        if not required.passed:
            raise ValueError("Missing required TLC columns")

        # Step 3: Normalize and add quality columns
        cleaned = add_quality_columns(normalize_columns(df))

        # Step 4: Mark invalid records
        cleaned = cleaned.withColumn(
            "_invalid_trip",
            F.coalesce(
                invalid_trip_condition(),
                F.lit(False),
            ),
        )

        # Step 5: Count input and invalid rows together
        counts = cleaned.agg(
            F.count("*").alias("input_records"),
            F.sum(F.when(F.col("_invalid_trip"), 1).otherwise(0)).alias("rejected_records"),
        ).first()

        input_count = int(counts["input_records"] or 0)
        invalid_count = int(counts["rejected_records"] or 0)

        LOGGER.info("input_records=%s", input_count)
        LOGGER.info("rejected_records=%s", invalid_count)

        if invalid_count > 0:
            LOGGER.warning(
                "Data quality warning: %s rejected records",
                invalid_count,
            )

        # Step 6: Separate valid and invalid data
        invalid = cleaned.filter(F.col("_invalid_trip")).drop("_invalid_trip")

        valid = cleaned.filter(~F.col("_invalid_trip")).drop("_invalid_trip")

        # Step 7: Remove duplicates
        valid = deduplicate(valid)

        # Step 8: Add business columns
        valid = add_business_columns(valid)

        # Step 9: Write rejected records
        if rejected_path and invalid_count > 0:
            LOGGER.info("Writing rejected records")

            (
                invalid.withColumn(
                    "rejection_reason",
                    F.lit("core_business_rule_failure"),
                )
                .coalesce(2)
                .write.mode("overwrite")
                .partitionBy("pickup_date")
                .parquet(rejected_path)
            )

        # Step 10: Write Silver data
        LOGGER.info("Writing Silver data")

        (valid.coalesce(2).write.mode("overwrite").partitionBy("pickup_date").parquet(output_path))

        # Step 11: Count completed Silver records
        output_count = spark.read.parquet(output_path).count()

        # Step 12: Calculate metrics
        duplicate_count = max(
            input_count - invalid_count - output_count,
            0,
        )

        if duplicate_count > 0:
            LOGGER.warning(
                "Duplicate records removed=%s",
                duplicate_count,
            )

        processing_time = round(
            time.perf_counter() - start_time,
            2,
        )

        metrics = {
            "pipeline_status": "SUCCESS",
            "input_records": input_count,
            "output_records": output_count,
            "rejected_records": invalid_count,
            "duplicate_records": duplicate_count,
            "processing_time_seconds": processing_time,
        }

        LOGGER.info("pipeline_metrics=%s", metrics)
        LOGGER.info("pipeline_status=SUCCESS")
        LOGGER.info(
            "processing_time_seconds=%s",
            processing_time,
        )

        return metrics

    except Exception:
        processing_time = round(
            time.perf_counter() - start_time,
            2,
        )

        LOGGER.exception(
            "pipeline_status=FAILED processing_time_seconds=%s",
            processing_time,
        )

        raise

    finally:
        if spark is not None:
            spark.stop()


def main() -> None:
    configure_logging()

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--rejected")

    args = parser.parse_args()

    metrics = run(
        args.input,
        args.output,
        args.rejected,
    )

    print(
        "AIRFLOW_PIPELINE_METRICS=" + json.dumps(metrics),
        flush=True,
    )


if __name__ == "__main__":
    main()
