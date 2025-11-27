"""
Monitoring Drift Retrain DAG
Triggered externally (e.g., by Cloud Function via Pub/Sub alert)
"""
from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import RunPipelineJobOperator
from airflow.models import Variable

PROJECT_ID = Variable.get("project_id")
REGION = Variable.get("region", default_var="us-central1")
BUCKET_NAME = Variable.get("bucket_name")
PIPELINE_ROOT = f"gs://{BUCKET_NAME}/pipeline_root"

default_args = {
    "owner": "airflow",
    "retries": 1,
}

with DAG(
    "monitoring_drift_retrain",
    default_args=default_args,
    description="Retrain model on drift detection",
    schedule_interval=None, # Triggered externally
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=["mlops", "retrain"],
) as dag:

    # Trigger Training Pipeline directly
    # In a real scenario, might want to re-run feature engineering too, 
    # but often we just retrain on the latest accumulated data.
    trigger_retrain = RunPipelineJobOperator(
        task_id="trigger_retrain_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        display_name="penguin-retrain-drift",
        template_path=f"{PIPELINE_ROOT}/penguin_pipeline.json",
        pipeline_root=PIPELINE_ROOT,
        parameter_values={
            "project": PROJECT_ID,
            "region": REGION,
            "bq_table": f"{PROJECT_ID}.mlops_factory.features_penguins"
        },
    )

    trigger_retrain
