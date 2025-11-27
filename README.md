# MLOps Factory Templates

Welcome to the **MLOps Factory**. This repository is a production-ready, opinionated template for building scalable MLOps pipelines on Google Cloud Platform. It implements the "Factory" pattern where:

* **Cloud Composer (Airflow)** is the **Factory Manager**, orchestrating the entire workflow.
* **Dataproc Serverless** is the **Heavy Machinery**, processing massive datasets efficiently.
* **Vertex AI** is the **Assembly Line**, training, evaluating, and deploying models.

## Features

* **Infrastructure as Code (Terraform)**: One-click deployment of the entire factory.
* **Serverless Data Processing**: PySpark jobs on Dataproc Serverless (no cluster management!).
* **Vertex AI Pipelines**: Reusable KFP v2 components for training and deployment.
* **Feature Store**: BigQuery-backed feature management.
* **Closed-Loop Monitoring**: Automatic retraining triggered by model drift alerts.
* **Smart Rate Limiting**: Prevents redundant pipeline runs to save costs.
* **CI/CD**: Cloud Build integration for automated testing and deployment.

## Architecture

The MLOps Factory uses a multi-trigger architecture with smart rate limiting to prevent redundant pipeline executions and optimize costs.

**[View Full Architecture Diagram](architecture/mlops-architecture.mermaid)** - Shows complete flow including:

* Multiple trigger sources (Scheduler, Cloud Build, Pub/Sub, Manual)
* Rate limiting decision logic (prevents redundant runs)
* Closed-loop monitoring and drift detection
* End-to-end data flow from raw data to deployed models

### Quick Overview

```mermaid
graph TD
    subgraph Factory Manager [Cloud Composer]
        DAG[Daily Pipeline DAG]
    end

    subgraph Heavy Machinery [Dataproc Serverless]
        Spark[Feature Engineering Job]
    end

    subgraph Assembly Line [Vertex AI]
        Pipeline[Training Pipeline]
        Registry[Model Registry]
        Endpoint[Prediction Endpoint]
    end

    subgraph Warehouse [Google Cloud Storage]
        Raw[Raw Data]
        Processed[Processed Data]
    end

    DAG -->|Triggers| Spark
    Spark -->|Reads| Raw
    Spark -->|Writes| Processed
    DAG -->|Triggers| Pipeline
    Pipeline -->|Reads| Processed
    Pipeline -->|Registers| Registry
    Pipeline -->|Deploys| Endpoint
```

> **Note:** This simplified view shows the core factory components. The full architecture includes rate limiting, monitoring, and multiple trigger sources. See [`architecture/mlops-architecture.mermaid`](architecture/mlops-architecture.mermaid) for complete details.

## Getting Started

### Prerequisites

* Google Cloud Project with Billing enabled.
* `gcloud` CLI installed and authenticated.
* `terraform` installed (>= 1.5).

### Deployment in 10 Minutes

1. **Clone the repository:**

    ```bash
    git clone https://github.com/sonikajanagill/mlops-factory-templates.git
    cd mlops-factory-templates
    ```

2. **Initialize Infrastructure:**

    ```bash
    cd terraform
    terraform init
    terraform apply -var="project_id=YOUR_PROJECT_ID"
    ```

    *Type `yes` when prompted.*

3. **Upload Assets:**
    The `cloudbuild.yaml` handles this automatically on push, or you can manually sync:

    ```bash
    # Get bucket name from terraform output
    export DAG_BUCKET=$(terraform output -raw composer_bucket)
    gsutil -m rsync -r ../dags/ gs://$DAG_BUCKET/dags/
    ```

4. **Run the Factory:**
    Go to the Airflow UI (link in Composer console) and trigger `mlops_factory_daily_pipeline`.

## Repository Structure

* `terraform/`: Infrastructure definitions (IAM, Storage, Composer, Vertex).
* `dags/`: Airflow DAGs for orchestration.
* `src/dataproc/`: PySpark jobs for data processing.
* `pipelines/`: Vertex AI Pipeline definitions and components.
* `functions/`: Cloud Functions for event-driven triggers.

## Cost Estimate

* **Cloud Composer 3**: ~$0.50/hour (small environment).
* **Dataproc Serverless**: Pay per second of execution.
* **Vertex AI**: Pay per training hour and node hour.
* **Estimated Total for Demo**: < $5.00 (if destroyed after use).

## For Smaller Teams: AutoMLOps

If this "Factory" architecture feels too heavy for your current needs, consider using **[Google Cloud AutoMLOps](https://github.com/GoogleCloudPlatform/automlops)**.

* **Best for:** Small teams, rapid prototyping, single data scientist.
* **Why:** It generates a lightweight CI/CD pipeline and KFP definitions automatically from your notebook code.
* **Path to Factory:** Start with AutoMLOps, then migrate to this "Factory" pattern as you scale to multiple pipelines and complex data dependencies.

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
