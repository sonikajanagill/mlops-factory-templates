"""
MLOps Factory Daily Pipeline
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import DataprocCreateBatchOperator
from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import RunPipelineJobOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from airflow.models import Variable

# Variables (should be Airflow Variables in prod)
PROJECT_ID = Variable.get("project_id")
REGION = Variable.get("region", default_var="us-central1")
BUCKET_NAME = Variable.get("bucket_name")
PIPELINE_ROOT = f"gs://{BUCKET_NAME}/pipeline_root"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False, # Enable in prod
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "mlops_factory_daily_pipeline",
    default_args=default_args,
    description="Daily MLOps Factory Pipeline",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["mlops", "factory"],
) as dag:

    # 1. Data Validation (Mock)
    validate_data = PythonOperator(
        task_id="validate_data",
        python_callable=lambda: print("Data validation passed.")
    )

    # 2. Feature Engineering (Dataproc Serverless)
    batch_config = {
        "pyspark_batch": {
            "main_python_file_uri": f"gs://{BUCKET_NAME}/src/dataproc/feature_engineering_job.py",
            "args": [
                "--input_path", f"gs://{BUCKET_NAME}/raw_data/penguins.csv",
                "--output_table", f"{PROJECT_ID}.mlops_factory.features_penguins"
            ],
        },
        "environment_config": {
            "execution_config": {
                "service_account_email": f"sa-dataproc@{PROJECT_ID}.iam.gserviceaccount.com",
                "subnetwork_uri": f"projects/{PROJECT_ID}/regions/{REGION}/subnetworks/default",
            },
        },
    }

    feature_eng = DataprocCreateBatchOperator(
        task_id="feature_engineering",
        project_id=PROJECT_ID,
        region=REGION,
        batch=batch_config,
        batch_id="penguin-features-{{ ds_nodash }}",
    )

    # 3. Train & Deploy (Vertex AI Pipeline)
    trigger_pipeline = RunPipelineJobOperator(
        task_id="trigger_training_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        display_name="penguin-training-daily",
        template_path=f"{PIPELINE_ROOT}/penguin_pipeline.json",
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            "project": PROJECT_ID,
            "region": REGION,
            "bq_table": f"{PROJECT_ID}.mlops_factory.features_penguins"
        },
    )

    validate_data >> feature_eng >> trigger_pipeline
