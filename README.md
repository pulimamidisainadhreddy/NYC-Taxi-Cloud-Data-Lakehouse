# NYC Taxi Cloud Data Lakehouse

[![CI](https://github.com/pulimamidisainadhreddy/NYC-Taxi-Cloud-Data-Lakehouse/actions/workflows/ci.yml/badge.svg)](https://github.com/pulimamidisainadhreddy/NYC-Taxi-Cloud-Data-Lakehouse/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![AWS](https://img.shields.io/badge/Cloud-AWS-orange)
![Apache Spark](https://img.shields.io/badge/Processing-Apache%20Spark-blue)
![Architecture](https://img.shields.io/badge/Architecture-Bronze--Silver--Gold-purple)

## Overview

An end-to-end **Cloud Data Engineering project** that processes millions of NYC Yellow Taxi records using **AWS S3, Apache Spark, Apache Airflow, dbt, Amazon Athena, PostgreSQL, and Power BI**.

The project implements a **Bronze–Silver–Gold lakehouse architecture**, covering raw data ingestion, distributed processing, data quality validation, SQL transformations, automated workflows, pipeline monitoring, and business intelligence.

It demonstrates practical skills in building, testing, monitoring, and analyzing cloud-based data pipelines.

### Project Highlights

| Metric | Verified Result |
|---|---:|
| Input Records | **3,475,226** |
| Valid Output Records | **3,330,663** |
| Rejected Records | **144,563** |
| Duplicate Records Reported | **0** |
| Pipeline Status | **SUCCESS** |
| Power BI Dashboard Pages | **3** |
| Automated Python Tests | **4 Passed** |
| GitHub Actions CI | **Passed** |

**Project focus:** Cloud Data Engineering • ETL/ELT • Distributed Processing • Data Quality • Orchestration • Analytics • CI

---

## 1. Architecture

The pipeline follows a layered architecture that separates raw data, cleaned data, and analytics-ready datasets.

```text
              NYC TLC Yellow Taxi Data
                     (Parquet)
                         |
                         v
                 Python Ingestion
                         |
                         v
                AWS S3 — BRONZE
                     Raw Data
                         |
                         v
                   Apache Spark
               Cleaning & Validation
                    /         \
                   v           v
             Valid Data    Rejected Data
                   |
                   v
                AWS S3 — SILVER
              Partitioned Parquet
                   |
                   v
               AWS Glue / Athena
                   |
                   v
                 dbt Models
          Staging → Intermediate → Marts
                   |
                   v
                 GOLD LAYER
             Analytics-Ready Data
                   |
                   v
                 Power BI
             3 Dashboard Pages


Additional Components
---------------------
Apache Airflow  → Workflow orchestration
PostgreSQL      → Pipeline execution metrics
Docker          → Containerized development
MinIO           → S3-compatible local storage
GitHub Actions  → Automated CI checks
```

**Architecture diagram:** A visual diagram can be added at `docs/images/architecture.png`.

The complete architecture combines cloud data storage, distributed transformations, SQL analytics, reporting, and pipeline observability.

---

## 2. Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python 3.11, SQL |
| Cloud Platform | AWS |
| Storage | Amazon S3, Parquet |
| Distributed Processing | Apache Spark, PySpark |
| Orchestration | Apache Airflow |
| SQL Transformation | dbt |
| Query Engine | Amazon Athena |
| Metadata Catalog | AWS Glue |
| Monitoring | PostgreSQL |
| Visualization | Power BI |
| Local Infrastructure | Docker, Docker Compose, MinIO |
| Testing | Pytest |
| Code Quality | Ruff, Black |
| Continuous Integration | GitHub Actions |
| Version Control | Git, GitHub |

---

## 3. Data Pipeline

### Bronze — Raw Data Ingestion

The Bronze layer stores original NYC TLC Yellow Taxi records.

- Download Parquet files from the official data source
- Ingest source data using Python
- Store raw datasets in AWS S3
- Preserve original records for reproducibility
- Support month-based ingestion

### Silver — Cleaning and Validation

Apache Spark transforms raw data into validated datasets.

- Apply data type transformations
- Validate trip values
- Identify invalid records
- Track rejected records separately
- Apply duplicate-handling logic
- Write cleaned records as partitioned Parquet

### Gold — Analytical Models

dbt organizes SQL transformations into reusable analytical models.

- Staging models prepare source data
- Intermediate models apply reusable business logic
- Mart models produce reporting-ready metrics
- Amazon Athena supports SQL-based analysis
- Power BI presents business insights

### Data Flow Summary

**Raw Parquet → AWS S3 Bronze → Spark → S3 Silver → Athena/dbt → Gold Analytics → Power BI**

---

## 4. Dataset and Processing Results

**Dataset:** [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

The project uses publicly available NYC Yellow Taxi data containing:

- Pickup and drop-off timestamps
- Passenger counts
- Trip distances
- Pickup and drop-off location IDs
- Fare amounts
- Payment types
- Total transaction amounts

### Successful Pipeline Run

| Metric | Result |
|---|---:|
| Source Records | 3,475,226 |
| Valid Records | 3,330,663 |
| Rejected Records | 144,563 |
| Duplicate Records Reported | 0 |
| Pipeline Status | SUCCESS |

These statistics represent one completed pipeline run, not the full NYC TLC dataset.

### Data Quality

The pipeline includes validation rules, duplicate handling, rejected-record tracking, and row-count monitoring.

**Relevant modules:**
- `src/quality/validation.py`
- `src/quality/validate_source.py`
- `src/quality/post_pipeline_check.py`

[Read Data Quality Documentation](docs/data_quality.md)

---

## 5. Apache Airflow Orchestration

Apache Airflow orchestrates the pipeline and tracks execution status.

### Executed Workflow

```text
Start
  |
  v
Spark Bronze-to-Silver Processing
  |
  v
Save Pipeline Metrics
  |
  v
dbt Build
  |
  v
Finish
```

### Airflow Features

- Automated workflow execution
- Task dependency management
- Execution logs
- Pipeline status tracking
- Runtime monitoring
- Spark and dbt integration

**DAG:** [`dags/cloud_data_pipeline.py`](dags/cloud_data_pipeline.py)

### Successful Airflow Execution

The project has completed a successful end-to-end Airflow workflow.

**Evidence:** Add a screenshot of the successful DAG execution at `docs/images/airflow-success.png`.

---

## 6. dbt and SQL Analytics

dbt is used to create modular and reusable SQL transformations.

| Model Layer | Purpose |
|---|---|
| Staging | Prepare source records |
| Intermediate | Apply reusable business logic |
| Marts | Create analytical datasets |

### Analytical Models

The repository includes:

- Daily trip metrics
- Hourly trip metrics
- Payment analysis
- Zone performance
- Trip fact data

### Example Business Questions

The analytical datasets support questions such as:

- How does taxi revenue change by day?
- Which hours have the highest trip demand?
- Which payment methods are used most frequently?
- Which pickup and drop-off zones perform best?

**Explore:**
- [dbt Models](dbt/models/)
- [dbt Tests](dbt/tests/)
- [SQL Analysis](sql/analysis/)
- [Athena SQL](sql/athena/)

---

## 7. Power BI Dashboards

Three Power BI report pages were developed to visualize business performance and pipeline operations.

### Dashboard 1 — Executive Overview

**Purpose:** Provide an overview of taxi business performance.

Key analysis areas:
- Business KPI summary
- Trip volume
- Revenue performance
- Operational trends

**Screenshot:** `docs/images/dashboard-1-executive.png`.

### Dashboard 2 — Trip Analysis

**Purpose:** Understand taxi demand and trip patterns.

Key analysis areas:
- Trip activity
- Time-based demand trends
- Trip characteristics
- Business insights

**Screenshot:**  `docs/images/dashboard-2-trips.png`.

### Dashboard 3 — Payments & Locations

**Purpose:** Analyze payment behavior, location performance, and pipeline monitoring.

Key analysis areas:
- Credit-card and cash trips
- Top pickup locations
- Top revenue locations
- Pipeline execution status
- Input, output, and rejected record counts
- Pipeline execution time

**Screenshot:** `docs/images/dashboard-3-payments.png`.

### Dashboard Data Refresh

Pipeline metrics are stored in PostgreSQL and can be refreshed separately in Power BI.

Some business visuals use exported Athena results and require an independent data refresh. Refreshing operational metrics does not automatically refresh the analytical dataset.

**Note:** Dashboard screenshots are not included in the repository yet. Add the actual exports before embedding them as images in this README.

---

## 8. Pipeline Monitoring

The project uses PostgreSQL to store pipeline execution metrics.

### Monitored Metrics

| Metric | Purpose |
|---|---|
| Pipeline Status | Identify successful or failed runs |
| Input Records | Track source volume |
| Output Records | Track valid processed data |
| Rejected Records | Monitor data quality |
| Duplicate Records | Track duplicate handling |
| Execution Time | Monitor runtime |

These metrics can be displayed in Power BI to provide operational visibility alongside business analytics.

This allows the project to demonstrate both **data engineering** and **pipeline observability**.

---

## 9. Repository Structure

```text
NYC-Taxi-Cloud-Data-Lakehouse/
│
├── .github/workflows/      # GitHub Actions CI
├── config/                 # Project configuration
├── dags/                   # Apache Airflow DAG
├── data/                   # Data documentation and samples
├── dbt/                    # dbt models, macros and tests
├── docs/                   # Project documentation
├── scripts/                # Setup and ingestion utilities
├── sql/                    # Analytical and Athena SQL
├── src/
│   ├── ingestion/          # Data ingestion
│   ├── quality/            # Data validation
│   ├── spark/              # Spark processing
│   └── utils/              # Logging and monitoring
├── tests/                  # Automated Python tests
├── .env.example            # Environment template
├── docker-compose.yml      # Container configuration
├── Dockerfile
├── Dockerfile.airflow
├── Dockerfile.spark
├── pyproject.toml
├── requirements.txt
├── README.md
└── LICENSE
```

---

## 10. Local Setup

### Requirements

- Python 3.11
- Docker Desktop
- Docker Compose
- Git
- Adequate memory for local Spark and Airflow services

### Step 1 — Clone the Repository

```bash
git clone https://github.com/pulimamidisainadhreddy/NYC-Taxi-Cloud-Data-Lakehouse.git
cd NYC-Taxi-Cloud-Data-Lakehouse
```

### Step 2 — Create a Python Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Configure the environment variables required for the intended local or cloud deployment.

Never commit actual credentials, passwords, AWS access keys, or `.env` files.

### Step 5 — Start Docker Services

```bash
docker compose up -d --build
docker compose ps
```

### Local Service URLs

| Service | URL |
|---|---|
| Airflow | http://localhost:8080 |
| MinIO Console | http://localhost:9001 |
| Spark UI | http://localhost:8081 |

These URLs depend on your active Docker configuration.

### Step 6 — Download Sample Data

```bash
python scripts/download_tlc_month.py --year 2025 --month 1
```

### Step 7 — Run Tests

```bash
python -m ruff check .
python -m black --check .
python -m pytest tests/ -q
```

The commands above cover the local development environment and automated checks. Running the full AWS pipeline requires additional cloud configuration.

For instructions, see:
- [Local Setup](docs/setup.md)
- [AWS Configuration](docs/aws.md)
- [Pipeline Guide](docs/pipeline.md)

---

## 11. Automated Testing and GitHub Actions

The project implements automated code quality and testing through GitHub Actions.

### Testing Tools

| Tool | Purpose | Verified Result |
|---|---|---|
| Ruff | Linting and code quality | Passed |
| Black | Python formatting | Passed |
| Pytest | Automated tests | 4 passed |
| GitHub Actions | Continuous integration | Passed |

### CI Workflow

```text
Git Push / Pull Request
         |
         v
   GitHub Actions
         |
         v
  Install Dependencies
         |
         v
    Ruff Check
         |
         v
    Black Check
         |
         v
       Pytest
         |
         v
    CI Pass / Fail
```

**Workflow:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

**Verified result:** The GitHub Actions `quality` job completed successfully.

[View GitHub Actions](https://github.com/pulimamidisainadhreddy/NYC-Taxi-Cloud-Data-Lakehouse/actions)

The current workflow performs **Continuous Integration (CI)**. Automated production deployment is not part of this workflow.

---

## 12. Engineering Practices

This project demonstrates several important Data Engineering practices.

| Practice | Implementation |
|---|---|
| Layered Architecture | Bronze, Silver, Gold |
| Cloud Storage | Amazon S3 |
| Distributed Processing | Apache Spark |
| Efficient Storage | Parquet and partitioning |
| Incremental Processing | Month-based processing |
| Data Quality | Validation and rejected-record tracking |
| Workflow Automation | Apache Airflow |
| SQL Modeling | dbt |
| Analytics | Amazon Athena and Power BI |
| Observability | PostgreSQL pipeline metrics |
| Version Control | Git and GitHub |
| Automated Quality Checks | Ruff, Black, Pytest, GitHub Actions |

Important design decisions are recorded in [Architecture Decision Records](docs/decisions/).

---

## 13. Documentation

| Documentation | Description |
|---|---|
| [Setup Guide](docs/setup.md) | Local environment setup |
| [AWS Guide](docs/aws.md) | Cloud configuration |
| [Pipeline Guide](docs/pipeline.md) | Data pipeline workflow |
| [Data Dictionary](docs/data_dictionary.md) | Dataset columns and meanings |
| [Data Quality](docs/data_quality.md) | Validation rules |
| [Runbook](docs/runbook.md) | Operational guidance |
| [Troubleshooting](docs/troubleshooting.md) | Common issues |
| [Architecture Decisions](docs/decisions/) | Engineering design choices |

---

## 14. Future Improvements

Planned enhancements include:

- Publish the visual architecture diagram and dashboard screenshots
- Expand automated integration test coverage
- Add more detailed pipeline alerts and monitoring
- Introduce Infrastructure as Code
- Add automated deployment workflows
- Improve historical performance monitoring

These are future improvements, not features claimed to be implemented already.

---

## Resume Summary

**NYC Taxi Cloud Data Lakehouse | AWS S3, PySpark, Airflow, dbt, Athena, Power BI**

- Built an end-to-end cloud data engineering pipeline using AWS S3, Apache Spark, Airflow, and dbt, following a Bronze–Silver–Gold architecture.
- Processed **3.47 million taxi records**, producing **3.33 million valid records** and tracking **144,563 rejected records** through data-quality validation.
- Developed SQL analytical models and three Power BI report pages covering business performance, trip analysis, payment trends, locations, and pipeline monitoring.
- Implemented automated code quality checks and **4 passing Python tests** through GitHub Actions CI.

---

## Data Source and License

**Dataset:** [NYC Taxi & Limousine Commission](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)

**Project License:** [LICENSE](LICENSE)

**GitHub Repository:** [NYC Taxi Cloud Data Lakehouse](https://github.com/pulimamidisainadhreddy/NYC-Taxi-Cloud-Data-Lakehouse)