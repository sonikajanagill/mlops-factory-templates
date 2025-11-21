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

from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import RunPipelineJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
import logging
import random

def check_execution_condition(**kwargs):
    """
    Decide whether to proceed with the pipeline or skip.
    Returns the task_id of the next task to run.
    """
    # Example logic: Randomly decide (for demo) or check a condition
    # In prod, you might check file size, specific flags, etc.
    should_run = True # Set to random.choice([True, False]) to test both paths
    
    if should_run:
        logging.info("Condition met. Proceeding with DataProc batch.")
        return "create_dataproc_batch"
    else:
        logging.info("Condition not met. Skipping processing.")
        return "skip_processing"

def notify_failure(context):
    """
    Callback function to send notifications on task failure.
    """
    task_instance = context['task_instance']
    task_id = task_instance.task_id
    dag_id = context['dag'].dag_id
    
    # TODO: Implement actual Email/Slack sending logic here
    # Example: send_slack_notification(...)
    logging.error(f"CRITICAL: Task {task_id} in DAG {dag_id} failed!")
    logging.info("Sending Slack/Email notification to operations team...")

def log_success(**kwargs):
    """
    Log success message after pipeline completion.
    """
    logging.info("Pipeline completed successfully. Model deployed and verified.")

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
    "on_failure_callback": notify_failure, # Trigger notification on any task failure
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



    # Step 1: Check if data exists in GCS
    check_data = GCSObjectsWithPrefixExistenceSensor(
        task_id="check_input_data",
        bucket=BUCKET_NAME,
        prefix="raw_data/",
        mode="poke",
        poke_interval=60,
        timeout=600, # Wait up to 10 minutes
    )

    # Step 2: Branching Logic (If/Else)
    branch_task = BranchPythonOperator(
        task_id="check_execution_condition",
        python_callable=check_execution_condition,
    )

    # Step 2b: Skip path
    skip_task = DummyOperator(
        task_id="skip_processing",
    )

    create_batch = DataprocCreateBatchOperator(
        task_id="create_dataproc_batch",
        project_id=PROJECT_ID,
        region=REGION,
        batch=batch_config,
        batch_id="batch-{{ ds_nodash }}-{{ ts_nodash }}", # Unique ID per run
        timeout=3600, # Timeout in seconds
    )

    # Trigger Vertex AI Pipeline
    trigger_pipeline = RunPipelineJobOperator(
        task_id="trigger_vertex_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        display_name="mlops-pipeline-trigger",
        template_path=f"gs://{BUCKET_NAME}/pipeline_root/mlops_pipeline.json", # Path to compiled pipeline JSON
        pipeline_root=f"gs://{BUCKET_NAME}/pipeline_root",
        parameter_values={
            "bq_table": "your-project.dataset.table",
            "project": PROJECT_ID,
            "region": REGION,
        },
    )

    # Step 4: Log success
    log_success_task = PythonOperator(
        task_id="log_success",
        python_callable=log_success,
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS, # Run if either path succeeds
    )


    # Define task dependencies
    check_data >> branch_task
    branch_task >> create_batch >> trigger_pipeline >> log_success_task
    branch_task >> skip_task >> log_success_task
