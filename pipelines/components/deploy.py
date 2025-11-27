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
        print(f"Model accuracy {accuracy:.4f} >= {threshold}. Deploying...")

        aiplatform.init(project=project, location=region)

        # Upload model
        uploaded_model = aiplatform.Model.upload(
            display_name="penguin-classifier",
            artifact_uri=model.uri.replace("/model", ""),  # Parent directory
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.1-0:latest"
        )
        print(f"Model uploaded: {uploaded_model.resource_name}")

        # Deploy to endpoint (reuse existing endpoint if available)
        endpoint_display_name = "penguin-endpoint"
        endpoints = aiplatform.Endpoint.list(
            filter=f'display_name="{endpoint_display_name}"',
            order_by="create_time desc"
        )

        if endpoints:
            endpoint = endpoints[0]
            print(f"Reusing existing endpoint: {endpoint.resource_name}")
        else:
            endpoint = aiplatform.Endpoint.create(display_name=endpoint_display_name)
            print(f"Created new endpoint: {endpoint.resource_name}")

        uploaded_model.deploy(
            endpoint=endpoint,
            machine_type="n1-standard-2",
            min_replica_count=1,
            max_replica_count=1,
            traffic_percentage=100
        )
        print("Model deployed successfully!")
    else:
        print(f"Model accuracy {accuracy:.4f} < {threshold}. Skipping deployment.")
