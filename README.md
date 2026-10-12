# NYC Taxi Cloud Data Lakehouse

Cloud data engineering portfolio project using NYC TLC Yellow Taxi data.

## Portfolio progression
- Project 1: Kafka + Spark Streaming -> Streaming Engineering
- Project 2: Python + PostgreSQL + Airflow -> Batch ETL
- Project 3: AWS S3 + Spark + Airflow + dbt -> Cloud Lakehouse

## Architecture
```text
NYC TLC Parquet
      |
      v
AWS S3 Bronze
      |
      v
Apache Spark ----> rejected records
      |
      v
AWS S3 Silver (partitioned Parquet)
      |
      v
Glue Catalog / Athena
      |
      v
      dbt
 staging -> intermediate -> marts
      |
      v
    Gold
      |
      v
  Power BI

Airflow = orchestration
Python  = ingestion/utilities
Docker  = local development
GitHub Actions = CI
```

## Main features
- Bronze/Silver/Gold lakehouse layers
- S3 and S3-compatible local development with MinIO
- Spark cleaning and validation
- Parquet + partitioning
- Month-based incremental processing
- Rejected-record handling
- dbt models and tests
- Airflow orchestration, retries and scheduling
- Athena SQL
- Structured logging and pipeline metrics
- Unit/integration tests
- GitHub Actions CI
- No secrets committed

## Dataset
Official NYC TLC Trip Record Data:
https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

Develop with 1-3 Yellow Taxi months first. Expand only after the complete pipeline works.

## Local setup
```bash
python -m pip install -r requirements.txt
cp .env.example .env
docker compose up -d --build
python scripts/download_tlc_month.py --year 2025 --month 1
pytest -q
ruff check .
black --check .
```

Local services:
- Airflow: http://localhost:8080
- MinIO: http://localhost:9001
- Spark UI: http://localhost:8081

## Cloud
See `docs/aws.md` for S3, IAM, Glue Catalog, Athena, MWAA and dbt deployment. The source code is cloud-ready, but actual AWS resources and credentials must be configured in your AWS account.

## Resume-ready summary
Built a cloud-based NYC taxi lakehouse using AWS S3, Apache Spark, Airflow and dbt, implementing Bronze/Silver/Gold layers, incremental processing, partitioned Parquet, data-quality validation, automated testing and SQL analytics.
