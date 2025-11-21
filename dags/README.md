# Airflow DAGs

This directory contains the DAGs that orchestrate the MLOps Factory.

## DAGs

*   **`mlops_factory_daily_pipeline.py`**: The main daily driver.
    1.  Validates input data.
    2.  Submits a Dataproc Serverless PySpark job for feature engineering.
    3.  Triggers the Vertex AI Training Pipeline.
*   **`monitoring_drift_retrain.py`**: Event-driven DAG.
    *   Triggered externally (e.g., by Cloud Function) when model drift is detected.
    *   Re-runs the training pipeline on new data.
