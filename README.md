# MLOps Factory Templates

> Topic: "From Data Chaos to Production AI"

This repository contains production-ready templates for building MLOps pipelines on Google Cloud Platform. It demonstrates modern architecture patterns using Cloud Composer (Airflow), Serverless DataProc, and Vertex AI Pipelines.

## Architecture

![MLOps Architecture](architecture/mlops-architecture.png)

The architecture follows a modular approach:
1.  **Orchestration**: Cloud Composer (Airflow) manages the end-to-end workflow.
2.  **Data Processing**: Serverless DataProc batches handle heavy data transformation tasks.
3.  **ML Workflow**: Vertex AI Pipelines manage the machine learning lifecycle (training, evaluation, deployment).
4.  **Artifacts**: GCS and Artifact Registry store data and models.

## Repository Structure

```
mlops-factory-templates/
├── README.md                    # This file
├── architecture/                # Architecture diagrams
│   └── mlops-architecture.mermaid
├── composer-dags/               # Airflow DAGs
│   └── dataproc_batch_dag.py    # Serverless DataProc orchestration
├── vertex-ai/                   # ML Pipeline definitions
│   └── pipeline.py              # Vertex AI Pipeline definition
└── docs/                        # Documentation
    ├── getting-started.md       # Setup and deployment guide
    ├── cost-optimization.md     # Cost saving strategies
    └── security-reliability.md  # Security and reliability best practices
```

## Quick Start

1.  **Clone this repository**:
    ```bash
    git clone https://github.com/your-org/mlops-factory-templates.git
    cd mlops-factory-templates
    ```

2.  **Set up your environment**:
    Follow the [Getting Started Guide](docs/getting-started.md) to configure your GCP project and development environment.

3.  **Deploy a Pipeline**:
    - Upload `composer-dags/dataproc_batch_dag.py` to your Cloud Composer DAGs bucket.
    - Compile and submit the Vertex AI pipeline using `vertex-ai/pipeline.py`.

## Key Features

-   **Serverless Data Processing**: Uses `DataprocCreateBatchOperator` to run Spark jobs without managing clusters.
-   **Vertex AI Integration**: Seamlessly triggers Vertex AI Pipelines from Airflow.
-   **Cost Optimized**: configured for preemptible instances and serverless execution.
-   **Enterprise Ready**: Includes error handling, retries, and security best practices.

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting a pull request.

## Contact

-   **Maintainer**: Sonika Janagill
