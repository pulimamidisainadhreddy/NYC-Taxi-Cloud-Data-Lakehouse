# Runbook

## Failure
1. Open the Airflow task log.
2. Identify the failing stage.
3. Check source availability and S3 permissions.
4. Check Spark logs.
5. Check Glue/Athena status.
6. Check dbt logs.
7. Fix the root cause.
8. Retry the failed month.

## Athena performance
- Avoid `SELECT *`.
- Filter by date/partition.
- Select only required columns.
- Prefer Parquet.

## Bad data
Inspect the rejected S3 prefix and its rejection reason before changing transformation rules.
