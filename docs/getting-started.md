# Getting Started

This guide will help you set up your environment and deploy the MLOps pipelines.

## Prerequisites

1.  **Google Cloud Project**: You need a GCP project with billing enabled.
2.  **APIs Enabled**:
    -   Cloud Composer API
    -   Cloud Dataproc API
    -   Vertex AI API
    -   Cloud Storage API
    -   Artifact Registry API
3.  **Tools Installed**:
    -   gcloud CLI
    -   Python 3.9+

## Setup Steps

### 1. Environment Configuration

Set your project ID and region variables:

```bash
export PROJECT_ID="your-project-id"
export REGION="us-central1"
export BUCKET_NAME="your-bucket-name"

gcloud config set project $PROJECT_ID
```

### 2. Create Cloud Storage Bucket

Create a bucket for your data and artifacts:

```bash
gsutil mb -l $REGION gs://$BUCKET_NAME
```

### 3. Deploy Cloud Composer DAG

1.  Create a Cloud Composer environment (if you haven't already).
2.  Upload the DAG file to the DAGs bucket:

```bash
gcloud composer environments storage dags import \
    --environment your-composer-env \
    --location $REGION \
    --source composer-dags/dataproc_batch_dag.py
```

### 4. Compile and Run Vertex AI Pipeline

1.  Install required packages:
    ```bash
    pip install google-cloud-aiplatform kfp
    ```
2.  Compile the pipeline:
    ```bash
    python vertex-ai/pipeline.py
    ```
    This will generate `mlops_pipeline.json`.
3.  Submit the pipeline to Vertex AI (you can also use the UI):
    ```python
    from google.cloud import aiplatform

    aiplatform.init(project=PROJECT_ID, location=REGION)

    job = aiplatform.PipelineJob(
        display_name="mlops-pipeline",
        template_path="mlops_pipeline.json",
        pipeline_root=f"gs://{BUCKET_NAME}/pipeline_root",
    )

    job.run()
    ```

## Next Steps

-   Explore [Cost Optimization](cost-optimization.md) strategies.
-   Review [Security & Reliability](security-reliability.md) best practices.
