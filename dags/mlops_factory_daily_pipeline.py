"""
"""
MLOps Factory Daily Pipeline
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import RunPipelineJobOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectsWithPrefixExistenceSensor
from airflow.operators.python import PythonOperator, BranchPythonOperator, ShortCircuitOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.trigger_rule import TriggerRule

from airflow.models import Variable
import logging

# Variables (should be Airflow Variables in prod)
PROJECT_ID = Variable.get("project_id")
REGION = Variable.get("region", default_var="us-central1")
BUCKET_NAME = Variable.get("bucket_name")
PIPELINE_ROOT = f"gs://{BUCKET_NAME}/pipeline_root"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['mlops-team@example.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def check_rate_limit(**context):
    """Checks if the pipeline has run recently to avoid redundant triggers."""
    MIN_HOURS = 5
    last_run_str = Variable.get("mlops_last_training_run", default_var=None)
    
    if not last_run_str:
        logging.info("No previous run recorded. Proceeding.")
        Variable.set("mlops_last_training_run", datetime.now().isoformat())
        return True
        
    last_run = datetime.fromisoformat(last_run_str)
    hours_since_last = (datetime.now() - last_run).total_seconds() / 3600
    
    if hours_since_last < MIN_HOURS:
        logging.warning(f"Rate limit active. Last run was {hours_since_last:.2f} hours ago. Min required: {MIN_HOURS}.")
        return False
        
    logging.info(f"Rate limit passed. Last run was {hours_since_last:.2f} hours ago.")
    Variable.set("mlops_last_training_run", datetime.now().isoformat())
    return True

with DAG(
    'mlops_factory_daily_pipeline',
    default_args=default_args,
    description='Daily MLOps pipeline with Dataproc and Vertex AI',
    schedule_interval='0 2 * * *', # Daily at 2 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['mlops', 'factory', 'production'],
) as dag:

    # 0. Rate Limit Check
    rate_limit_check = ShortCircuitOperator(
        task_id="check_rate_limit",
        python_callable=check_rate_limit
    )

    # 1. Check if data exists
    check_data_sensor = GCSObjectsWithPrefixExistenceSensor(
        task_id='check_raw_data_exists',
        bucket=BUCKET_NAME,
        prefix='raw_data/',
        mode='poke',
        timeout=600,
        poke_interval=60
    )

    # 2. Conditional Logic: Should we process data?
    def check_data_freshness(**kwargs):
        # Placeholder logic: In prod, check file timestamps
        return 'create_batch'

    branch_task = BranchPythonOperator(
        task_id='check_freshness_branch',
        python_callable=check_data_freshness
    )

    # 3. Dataproc Serverless Batch Job
    BATCH_ID = "feature-eng-{{ ts_nodash }}"
    
    create_batch = DataprocCreateBatchOperator(
        task_id="create_batch",
        project_id=PROJECT_ID,
        region=REGION,
        batch= {
            "pyspark_batch": {
                "main_python_file_uri": f"gs://{BUCKET_NAME}/src/dataproc/feature_engineering_job.py",
                "args": [
                    f"--input_path=gs://{BUCKET_NAME}/raw_data/penguins.csv",
                    f"--output_table={PROJECT_ID}.mlops_factory.features_penguins"
                ],
                "jar_file_uris": ["gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar"]
            },
            "environment_config": {
                "execution_config": {
                    "service_account_email": f"sa-dataproc@{PROJECT_ID}.iam.gserviceaccount.com"
                }
            }
        },
        batch_id=BATCH_ID,
    )

    # 4. Trigger Vertex AI Pipeline
    trigger_pipeline = RunPipelineJobOperator(
        task_id="trigger_vertex_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        display_name="penguin-training-pipeline",
        template_path=f"gs://{BUCKET_NAME}/pipeline_root/penguin_pipeline.json",
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            "project_id": PROJECT_ID,
            "feature_table": f"{PROJECT_ID}.mlops_factory.features_penguins"
        },
    )

    # 5. Success/Failure Handling
    def notify_failure(context):
        logging.error(f"Task failed: {context['task_instance_key_str']}")
        # Add Slack/Email notification logic here

    def log_success(**kwargs):
        logging.info("Pipeline completed successfully!")

    log_success_task = PythonOperator(
        task_id='log_success',
        python_callable=log_success,
        trigger_rule=TriggerRule.ALL_SUCCESS
    )

    skip_processing = EmptyOperator(task_id='skip_processing')

    # Define Dependencies
    rate_limit_check >> check_data_sensor >> branch_task
    branch_task >> create_batch >> trigger_pipeline >> log_success_task
    branch_task >> skip_processing
