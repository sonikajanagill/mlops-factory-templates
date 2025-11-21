from kfp.v2.dsl import component, Input, Model

@component(
    base_image="google/cloud-sdk:latest",
    packages_to_install=["google-cloud-aiplatform"]
)
def conditional_deploy(
    model: Input[Model],
    project: str,
    region: str,
    accuracy: float,
    threshold: float = 0.7
):
    from google.cloud import aiplatform

    if accuracy >= threshold:
        print(f"Model accuracy {accuracy} >= {threshold}. Deploying...")
        
        aiplatform.init(project=project, location=region)
        
        # Upload model
        uploaded_model = aiplatform.Model.upload(
            display_name="penguin-classifier",
            artifact_uri=model.uri.replace("/model", ""), # Parent directory
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
        )
        
        # Deploy to endpoint
        endpoint = aiplatform.Endpoint.create(display_name="penguin-endpoint")
        uploaded_model.deploy(
            endpoint=endpoint,
            machine_type="n1-standard-2",
            min_replica_count=1,
            max_replica_count=1
        )
    else:
        print(f"Model accuracy {accuracy} < {threshold}. Skipping deployment.")
