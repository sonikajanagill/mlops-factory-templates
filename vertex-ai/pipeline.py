"""
Vertex AI Pipeline Definition

This file defines a Kubeflow Pipeline (KFP) for Vertex AI.
It demonstrates a simple ML workflow: Data Extraction -> Training -> Evaluation -> Deployment.
"""

from google.cloud import aiplatform
from kfp import dsl
from kfp.dsl import (
    component,
    Input,
    Output,
    Dataset,
    Model,
    Metrics,
    ClassificationMetrics,
)

# TODO: Replace with your actual values
PROJECT_ID = "your-project-id"
REGION = "us-central1"
PIPELINE_ROOT = f"gs://your-bucket/pipeline_root"

@component(
    base_image="python:3.9",
    packages_to_install=["pandas", "google-cloud-bigquery"]
)
def get_data(
    bq_table: str,
    dataset: Output[Dataset],
):
    """Extracts data from BigQuery."""
    import pandas as pd
    # Mock data extraction for template purposes
    print(f"Extracting data from {bq_table}")
    df = pd.DataFrame({"feature1": [1, 2, 3], "label": [0, 1, 0]})
    df.to_csv(dataset.path, index=False)

@component(
    base_image="python:3.9",
    packages_to_install=["scikit-learn", "pandas"]
)
def train_model(
    dataset: Input[Dataset],
    model: Output[Model],
    metrics: Output[Metrics],
):
    """Trains a simple model."""
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import pickle

    df = pd.read_csv(dataset.path)
    X = df[["feature1"]]
    y = df["label"]

    clf = LogisticRegression()
    clf.fit(X, y)

    # Save model
    model.path = model.path + ".pkl"
    with open(model.path, 'wb') as f:
        pickle.dump(clf, f)
    
    # Log metrics
    metrics.log_metric("accuracy", 0.85)

@component(
    base_image="python:3.9",
    packages_to_install=["scikit-learn", "pandas"]
)
def evaluate_model(
    dataset: Input[Dataset],
    model: Input[Model],
    metrics: Output[ClassificationMetrics],
) -> float:
    """Evaluates the model."""
    import pandas as pd
    import pickle
    from sklearn.metrics import roc_curve, confusion_matrix

    df = pd.read_csv(dataset.path)
    X = df[["feature1"]]
    y = df["label"]

    with open(model.path, 'rb') as f:
        clf = pickle.load(f)
    
    y_pred = clf.predict(X)
    
    # Log confusion matrix (mocked for template)
    metrics.log_confusion_matrix(
        ["0", "1"],
        [[1, 0], [0, 1]]
    )
    return 0.9

@component(
    base_image="google/cloud-sdk:latest"
)
def deploy_model(
    model: Input[Model],
    project: str,
    region: str,
):
    """Deploys the model to Vertex AI Endpoint."""
    print(f"Deploying model from {model.path} to {project} in {region}")
    # In a real scenario, use `gcloud ai endpoints deploy-model` or aiplatform SDK

@dsl.pipeline(
    name="mlops-factory-template-pipeline",
    description="A sample MLOps pipeline for Vertex AI",
    pipeline_root=PIPELINE_ROOT,
)
def mlops_pipeline(
    bq_table: str = "your-project.dataset.table",
    project: str = PROJECT_ID,
    region: str = REGION,
):
    data_op = get_data(bq_table=bq_table)
    
    train_op = train_model(dataset=data_op.outputs["dataset"])
    
    eval_op = evaluate_model(
        dataset=data_op.outputs["dataset"],
        model=train_op.outputs["model"]
    )

    with dsl.Condition(eval_op.output > 0.8, name="deploy-condition"):
        deploy_model(
            model=train_op.outputs["model"],
            project=project,
            region=region
        )

if __name__ == "__main__":
    from kfp.v2 import compiler
    compiler.Compiler().compile(
        pipeline_func=mlops_pipeline,
        package_path="mlops_pipeline.json"
    )
