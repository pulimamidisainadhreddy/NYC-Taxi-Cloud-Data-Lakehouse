# AWS Deployment Guide

## 1. S3
Create one private bucket, for example `nyc-taxi-lake-<unique-name>`.

Prefixes:
```text
bronze/yellow_taxi/
silver/yellow_taxi/
gold/
rejected/yellow_taxi/
athena-results/
```

Keep Block Public Access enabled and enable encryption. Do not commit credentials.

## 2. IAM
Use separate developer and runtime identities. The runtime role should use least privilege.

Typical S3 permissions:
- `s3:ListBucket`
- `s3:GetObject`
- `s3:PutObject`
- `s3:DeleteObject` only if the pipeline really needs it

Athena:
- `athena:StartQueryExecution`
- `athena:GetQueryExecution`
- `athena:GetQueryResults`
- `athena:StopQueryExecution` if operationally needed

Glue permissions depend on whether the pipeline creates/updates Catalog objects. For a managed catalog workflow, grant only the database/table/catalog actions required by the chosen deployment.

CloudWatch logging permissions are required by the runtime service used for orchestration.

## 3. Glue Catalog
Create database `nyc_taxi`. Register the Silver Parquet path as an external table using a Glue crawler or explicit Athena DDL. For a stable portfolio project, explicit DDL is easier to understand and control.

## 4. Athena
Create an Athena workgroup and configure query results under `s3://<bucket>/athena-results/`. Run `sql/athena/00_create_database.sql` and `01_silver_external_table.sql` after replacing the bucket name.

## 5. Airflow
**Recommended managed option:** Amazon MWAA. Create an MWAA environment in a suitable VPC/subnets, configure an execution role, and point the environment at an S3 DAG/plugins location. Upload `dags/cloud_data_pipeline.py` and configure the required environment variables/connections.

**Learning alternative:** run Airflow in Docker locally or on EC2. EC2 is self-managed and requires you to operate the host, scheduler, webserver, metadata DB and security updates.

## 6. dbt
For Athena, use `dbt-athena-community`. Set the `athena` target in `dbt/profiles.yml` and supply `ATHENA_OUTPUT_S3`, `AWS_REGION`, `ATHENA_DATABASE` and `ATHENA_WORKGROUP` through the runtime secret/configuration system.

Do not commit AWS access keys or a production `profiles.yml` containing secrets.

## 7. Cloud Spark execution
For a learning portfolio, run Spark locally while developing and document the cloud execution design. If you want a fully cloud-executed version, run the same Spark job on an AWS-managed Spark environment such as AWS Glue or a controlled Spark cluster. Keep the processing code independent of the execution environment.

## 8. Cost control
Start with 1-3 months. Stop unused compute. Use Parquet, partitions and column selection to reduce Athena scans. Add S3 lifecycle policies for temporary data.
