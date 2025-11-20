# Cost Optimization

Running MLOps pipelines can be expensive if not managed correctly. This guide outlines strategies to optimize costs for this repository's architecture.

## Serverless DataProc

We use **Serverless DataProc** (`DataprocCreateBatchOperator`) which inherently optimizes costs by:
-   **No Idle Clusters**: You only pay for the duration of the job. There are no long-running clusters to manage or forget to turn off.
-   **Auto-Scaling**: Resources scale up and down automatically based on the workload.

### Further Optimization
-   **Spot Instances**: Serverless DataProc supports Spot instances (Premium tier). You can configure this in the `batch_config` to significantly reduce compute costs (up to 60-91%).
    ```python
    # In dataproc_batch_dag.py
    "runtime_config": {
        "properties": {
            "spark.dynamicAllocation.enabled": "true",
            "spark.executor.instances": "2"
        }
    }
    ```

## Vertex AI Pipelines

-   **Caching**: Vertex AI Pipelines automatically caches successful steps. If you re-run a pipeline and the inputs haven't changed, it will reuse the previous output, saving time and compute.
-   **Machine Types**: Configure appropriate machine types for each component. Don't use a GPU for simple data processing tasks.
    ```python
    @component(base_image="python:3.9")
    def simple_task(...):
        ...
    # No special machine spec needed, runs on default (low cost)
    ```

## Cloud Storage

-   **Lifecycle Policies**: Set up lifecycle policies on your GCS buckets to automatically delete old temporary data or move it to cheaper storage classes (Nearline/Coldline) after a certain period.

## Monitoring

-   **Budgets & Alerts**: Always set up a budget in the Google Cloud Console and configure alerts to notify you when spending exceeds a threshold.
