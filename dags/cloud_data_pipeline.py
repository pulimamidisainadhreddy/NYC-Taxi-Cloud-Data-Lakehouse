from datetime import datetime, timedelta
import html
import json
import logging
import os

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.session import create_session
from sqlalchemy import text


LOGGER = logging.getLogger(__name__)


# ----------------------------------------
# Monitoring and failure alert functions
# ----------------------------------------


def task_duration(context):
    """Return task execution time in seconds."""
    ti = context.get("task_instance")

    if ti and ti.start_date and ti.end_date:
        return round(
            (ti.end_date - ti.start_date).total_seconds(),
            2,
        )

    return None


def task_success_callback(context):
    """Log successful task execution."""
    ti = context["task_instance"]

    LOGGER.info(
        "task_status=SUCCESS dag_id=%s task_id=%s " "run_id=%s duration_seconds=%s",
        ti.dag_id,
        ti.task_id,
        context.get("run_id"),
        task_duration(context),
    )


def task_retry_callback(context):
    """Log task retries."""
    ti = context["task_instance"]

    LOGGER.warning(
        "task_status=RETRY dag_id=%s task_id=%s " "run_id=%s attempt=%s error=%s",
        ti.dag_id,
        ti.task_id,
        context.get("run_id"),
        ti.try_number,
        context.get("exception"),
    )


def task_failure_callback(context):
    """Log task failure and send optional email alert."""
    ti = context["task_instance"]
    error = context.get("exception")

    LOGGER.error(
        "task_status=FAILED dag_id=%s task_id=%s " "run_id=%s duration_seconds=%s error=%s",
        ti.dag_id,
        ti.task_id,
        context.get("run_id"),
        task_duration(context),
        error,
    )

    alert_email = os.getenv("PIPELINE_ALERT_EMAIL")

    if not alert_email:
        LOGGER.warning("failure_alert=SKIPPED " "reason=PIPELINE_ALERT_EMAIL_not_configured")
        return

    subject = f"Airflow Pipeline Failed: " f"{ti.dag_id} / {ti.task_id}"

    message = (
        "<h3>NYC Taxi Cloud Lakehouse - Task Failure</h3>"
        f"<p><b>DAG:</b> {html.escape(ti.dag_id)}</p>"
        f"<p><b>Task:</b> {html.escape(ti.task_id)}</p>"
        f"<p><b>Run:</b> "
        f"{html.escape(str(context.get('run_id')))}</p>"
        f"<p><b>Error:</b> "
        f"{html.escape(str(error))}</p>"
    )

    try:
        from airflow.utils.email import send_email

        send_email(
            to=alert_email,
            subject=subject,
            html_content=message,
        )

        LOGGER.info(
            "failure_alert=SENT task_id=%s",
            ti.task_id,
        )

    except Exception:
        LOGGER.exception(
            "failure_alert=FAILED task_id=%s",
            ti.task_id,
        )


def pipeline_success_callback(context):
    """Log successful completion of the whole DAG."""
    dag_run = context["dag_run"]

    LOGGER.info(
        "pipeline_status=SUCCESS dag_id=%s run_id=%s",
        dag_run.dag_id,
        dag_run.run_id,
    )


def pipeline_failure_callback(context):
    """Log failure of the whole DAG."""
    dag_run = context["dag_run"]

    LOGGER.error(
        "pipeline_status=FAILED dag_id=%s run_id=%s",
        dag_run.dag_id,
        dag_run.run_id,
    )


# ----------------------------------------
# Save Spark metrics to PostgreSQL
# ----------------------------------------


def save_pipeline_metrics(**context):
    """Save Spark metrics to the Airflow PostgreSQL database."""

    raw = context["ti"].xcom_pull(task_ids="spark_bronze_to_silver")

    prefix = "AIRFLOW_PIPELINE_METRICS="

    if not isinstance(raw, str) or not raw.strip().startswith(prefix):
        raise ValueError("Spark metrics not found in Airflow XCom")

    metrics = json.loads(raw.strip()[len(prefix) :])

    parameters = {
        "dag_id": context["dag"].dag_id,
        "run_id": context["run_id"],
        "input_records": metrics["input_records"],
        "output_records": metrics["output_records"],
        "rejected_records": metrics["rejected_records"],
        "duplicate_records": metrics["duplicate_records"],
        "processing_time_seconds": metrics["processing_time_seconds"],
    }

    with create_session() as session:
        session.execute(
            text(
                """
                INSERT INTO public.powerbi_pipeline_metrics (
                    dag_id,
                    run_id,
                    input_records,
                    output_records,
                    rejected_records,
                    duplicate_records,
                    processing_time_seconds
                )
                VALUES (
                    :dag_id,
                    :run_id,
                    :input_records,
                    :output_records,
                    :rejected_records,
                    :duplicate_records,
                    :processing_time_seconds
                )
                ON CONFLICT (dag_id, run_id)
                DO UPDATE SET
                    input_records = EXCLUDED.input_records,
                    output_records = EXCLUDED.output_records,
                    rejected_records = EXCLUDED.rejected_records,
                    duplicate_records = EXCLUDED.duplicate_records,
                    processing_time_seconds = EXCLUDED.processing_time_seconds,
                    recorded_at = NOW()
            """
            ),
            parameters,
        )

    LOGGER.info(
        "pipeline_metrics_saved=SUCCESS dag_id=%s run_id=%s",
        parameters["dag_id"],
        parameters["run_id"],
    )


# ----------------------------------------
# Airflow configuration
# ----------------------------------------

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "on_success_callback": task_success_callback,
    "on_retry_callback": task_retry_callback,
    "on_failure_callback": task_failure_callback,
}

S3_BUCKET = "nyc-taxi-lakehouse-722769296222"

PIPELINE_VENV = "/home/airflow/pipeline-venv"

BRONZE_PATH = f"s3a://{S3_BUCKET}/bronze/yellow_taxi/2025/01/" "yellow_tripdata_2025-01.parquet"

SILVER_PATH = f"s3a://{S3_BUCKET}/silver/yellow_taxi/2025/01"

REJECTED_PATH = f"s3a://{S3_BUCKET}/rejected/yellow_taxi/2025/01"

ATHENA_RESULTS = f"s3://{S3_BUCKET}/athena-results/"


# ----------------------------------------
# Spark execution command
# ----------------------------------------

SPARK_COMMAND = (
    f"PYTHONPATH=/opt/project "
    f"{PIPELINE_VENV}/bin/spark-submit "
    f"--conf spark.pyspark.driver.python={PIPELINE_VENV}/bin/python "
    "--conf spark.pyspark.python=/usr/local/bin/python3 "
    "--master spark://spark-master:7077 "
    "--total-executor-cores 2 "
    "--executor-cores 2 "
    "--driver-memory 768m "
    "--executor-memory 1g "
    "--jars "
    "/opt/spark-jars/hadoop-aws-3.3.4.jar,"
    "/opt/spark-jars/aws-java-sdk-bundle-1.12.262.jar "
    "/opt/project/src/spark/bronze_to_silver.py "
    f"--input {BRONZE_PATH} "
    f"--output {SILVER_PATH} "
    f"--rejected {REJECTED_PATH}"
)


# ----------------------------------------
# Airflow DAG
# ----------------------------------------

with DAG(
    dag_id="nyc_taxi_cloud_lakehouse",
    start_date=datetime(2025, 1, 1),
    schedule="@monthly",
    catchup=False,
    max_active_runs=1,
    default_args=DEFAULT_ARGS,
    on_success_callback=pipeline_success_callback,
    on_failure_callback=pipeline_failure_callback,
    tags=["nyc-taxi", "spark", "dbt", "lakehouse"],
) as dag:

    # Step 1: Start pipeline
    start = EmptyOperator(
        task_id="start",
    )

    # Step 2: Spark Bronze to Silver
    spark_silver = BashOperator(
        task_id="spark_bronze_to_silver",
        bash_command=(
            "set -eo pipefail\n"
            f"source {PIPELINE_VENV}/bin/activate\n"
            "export AWS_SHARED_CREDENTIALS_FILE=/root/.aws/credentials\n"
            "cd /opt/project\n"
            "metrics_log=$(mktemp)\n"
            "trap 'rm -f \"$metrics_log\"' EXIT\n"
            f'{SPARK_COMMAND} 2>&1 | tee "$metrics_log"\n'
            "metrics_line=$(grep '^AIRFLOW_PIPELINE_METRICS=' "
            '"$metrics_log" | tail -n 1 || true)\n'
            'if [ -z "$metrics_line" ]; then\n'
            "    echo 'ERROR: Spark metrics were not found' >&2\n"
            "    exit 1\n"
            "fi\n"
            "printf '%s\\n' \"$metrics_line\"\n"
        ),
        do_xcom_push=True,
    )

    # Step 3: Save Spark metrics to PostgreSQL
    save_metrics = PythonOperator(
        task_id="save_pipeline_metrics",
        python_callable=save_pipeline_metrics,
    )

    # Step 4: Build Gold tables using dbt
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"source {PIPELINE_VENV}/bin/activate && "
            "unset PYTHONPATH && "
            "export PYTHONNOUSERSITE=1 && "
            "export AWS_SHARED_CREDENTIALS_FILE=/root/.aws/credentials && "
            "cd /opt/project/dbt && "
            "DBT_PROFILES_DIR=/opt/project/dbt "
            f"ATHENA_OUTPUT_S3={ATHENA_RESULTS} "
            "AWS_REGION=eu-central-1 "
            f"{PIPELINE_VENV}/bin/dbt build --target athena "
            "--profiles-dir /opt/project/dbt"
        ),
    )

    # Step 5: Finish pipeline
    finish = EmptyOperator(
        task_id="finish",
    )

    # Pipeline order
    start >> spark_silver >> save_metrics >> dbt_build >> finish
