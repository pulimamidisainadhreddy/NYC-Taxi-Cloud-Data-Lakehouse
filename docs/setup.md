# Setup

## Local
Prerequisites: Docker Desktop, Python 3.11+, Git.

```bash
python -m pip install -r requirements.txt
cp .env.example .env
python scripts/download_tlc_month.py --year 2025 --month 1
docker compose up -d --build
```

Run Spark:
```bash
docker compose exec spark-master spark-submit --master spark://spark-master:7077 /opt/project/src/spark/bronze_to_silver.py --input /opt/project/data/sample --output /opt/project/local-lake/silver --rejected /opt/project/local-lake/rejected
```

Run local dbt:
```bash
docker compose exec airflow bash -lc 'cd /opt/project/dbt && dbt build --profiles-dir /opt/project/dbt'
```

## Cloud
Configure S3, IAM, Glue and Athena using `docs/aws.md`, then set the Athena target in dbt and deploy the DAG to MWAA or another Airflow runtime.
