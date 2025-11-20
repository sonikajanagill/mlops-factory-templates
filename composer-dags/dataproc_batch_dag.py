"""
Serverless DataProc Batch DAG

This DAG demonstrates how to submit a serverless Spark batch job using Cloud Composer (Airflow).
It uses the `DataprocCreateBatchOperator` to create and submit the batch workload.

Key Features:
- Serverless execution (no cluster management)
- Cost optimization via auto-scaling and auto-termination (inherent to serverless)
- Error handling and retries
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.utils.trigger_rule import TriggerRule

# TODO: Replace with your actual values
PROJECT_ID = "your-project-id"
REGION = "us-central1"
BUCKET_NAME = "your-gcs-bucket"
PHS_CLUSTER_PATH = f"projects/{PROJECT_ID}/regions/{REGION}/clusters/phs-cluster" # Optional: Persistent History Server

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "serverless_dataproc_batch",
    default_args=default_args,
    description="Submit a Serverless Spark Batch Job",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["mlops", "dataproc", "serverless"],
) as dag:

    # Define the batch workload configuration
    batch_config = {
        "pyspark_batch": {
            "main_python_file_uri": f"gs://{BUCKET_NAME}/jobs/process_data.py",
            "args": [
                "--input", f"gs://{BUCKET_NAME}/raw_data/",
                "--output", f"gs://{BUCKET_NAME}/processed_data/"
            ],
            "jar_file_uris": [],
            "file_uris": [],
        },
        "runtime_config": {
            "version": "2.0",  # Spark runtime version
            # "container_image": "gcr.io/..." # Optional custom container
        },
        "environment_config": {
            "execution_config": {
                "service_account_email": f"dataproc-sa@{PROJECT_ID}.iam.gserviceaccount.com",
                "subnetwork_uri": f"projects/{PROJECT_ID}/regions/{REGION}/subnetworks/default",
            },
            # "peripherals_config": {
            #     "spark_history_server_config": {
            #         "dataproc_cluster": PHS_CLUSTER_PATH
            #     }
            # }
        },
    }

    create_batch = DataprocCreateBatchOperator(
        task_id="create_dataproc_batch",
        project_id=PROJECT_ID,
        region=REGION,
        batch=batch_config,
        batch_id="batch-{{ ds_nodash }}-{{ ts_nodash }}", # Unique ID per run
        timeout=3600, # Timeout in seconds
    )

    # Example of a downstream task (e.g., triggering a Vertex AI Pipeline)
    # trigger_pipeline = ...

    create_batch
