from kfp import dsl
from google.cloud.aiplatform import PipelineJob
from google_cloud_pipeline_components.v1.model_evaluation import ModelEvaluationOp

# Placeholders for training functions
def train_with_vertex_ai(dataset_path, hyperparameters):
    class Model:
        loss = 0.1
    return Model()

def evaluate_model(model):
    return 0.95

@dsl.component(base_image="us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-13:latest")
def train_model(dataset_path: str, model_output_path: str, hyperparameters: dict) -> tuple[str, float]:
    """Train ML model with native Vertex AI experiment tracking"""
    from google.cloud import aiplatform
    with aiplatform.start_run(run="training-run") as run:
        model = train_with_vertex_ai(dataset_path, hyperparameters)
        accuracy = evaluate_model(model)
        # Native experiment tracking
        run.log_metrics({"accuracy": accuracy, "loss": model.loss})
        run.log_params(hyperparameters)
        model_resource = aiplatform.Model.upload(
            display_name="ml-model",
            artifact_uri=model_output_path,
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-13:latest"
        )
        return model_resource.resource_name, accuracy

@dsl.pipeline(name="ml-training-pipeline")
def ml_pipeline(dataset_path: str, hyperparameters: dict):
    train_task = train_model(dataset_path=dataset_path, hyperparameters=hyperparameters)
    # Built-in evaluation with zero configuration
    eval_task = ModelEvaluationOp(
        project="your-project",
        model=train_task.outputs["model_resource_name"],
        target_field_name="target",
        prediction_type="classification"
    )
