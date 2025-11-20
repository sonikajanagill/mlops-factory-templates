# Security & Reliability

## Security

### Identity and Access Management (IAM)

-   **Least Privilege**: Assign granular roles to Service Accounts.
    -   **Composer SA**: Should only have access to manage DAGs and trigger DataProc/Vertex AI.
    -   **DataProc SA**: Should only have read/write access to specific GCS buckets and BigQuery datasets.
    -   **Vertex AI SA**: Should have access to Container Registry and specific GCS paths.
-   **Service Account Isolation**: Do not use the default Compute Engine service account. Create dedicated service accounts for each component.

### Network Security

-   **VPC Service Controls**: Use VPC Service Controls to define a security perimeter around your resources (GCS, BigQuery, Vertex AI) to prevent data exfiltration.
-   **Private IP**: Configure Cloud Composer and DataProc to use Private IP addresses to keep traffic within the Google network.

## Reliability

### Error Handling & Retries

-   **Airflow Retries**: The DAG is configured with `retries` and `retry_delay`.
    ```python
    default_args = {
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    }
    ```
-   **Pipeline Robustness**: Vertex AI Pipelines handle component failures. Ensure your components are idempotent where possible.

### Monitoring & Alerting

-   **Cloud Monitoring**: Set up dashboards to monitor:
    -   DAG failure rates.
    -   Pipeline duration and status.
    -   DataProc batch job errors.
-   **Email Alerts**: Configure `email_on_failure` in Airflow to get notified immediately when a critical DAG fails.

### Version Control

-   **Infrastructure as Code**: Use Terraform (not included in this template but recommended) to provision resources.
-   **Pipeline Versioning**: Vertex AI Pipelines supports versioning. Always tag your pipeline runs and model versions.
