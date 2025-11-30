# Infrastructure as Code (Terraform)

This directory contains the Terraform configuration to deploy the MLOps Factory infrastructure.

## Modules

*   **project-setup**: Enables required Google Cloud APIs.
*   **iam**: Creates Service Accounts with least-privilege roles.
    *   `sa-composer`: For Cloud Composer environment.
    *   `sa-dataproc`: For Dataproc Serverless jobs.
    *   `sa-vertex-pipeline`: For Vertex AI Pipelines.
*   **storage**: Creates GCS buckets for data and artifacts.
*   **composer**: Deploys Cloud Composer 3 environment.
*   **vertex-ai**: Sets up Feature Store and Artifact Registry.
*   **monitoring**: Configures Alert Policies and Notification Channels.
*   **wif_aws**: Configures Workload Identity Federation for AWS (Pool, Provider, SA impersonation).
*   **wif_azure**: Configures Workload Identity Federation for Azure (Pool, Provider via OIDC).

## Usage

```bash
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID"
terraform apply -var="project_id=YOUR_PROJECT_ID"
```
