"""
Vertex AI Training with CMEK (Customer Managed Encryption Keys)
Complete example for healthcare/compliance workloads

This script demonstrates:
- Initializing Vertex AI with CMEK configuration
- Creating a custom training job with encryption
- Deploying a model with CMEK
- Accessing prediction endpoints with encrypted artifacts
"""

from google.cloud import aiplatform
from google.cloud import storage
import os
from typing import Optional


def initialize_vertex_with_cmek(
    project_id: str,
    location: str,
    encryption_spec_key_name: str,
) -> None:
    """
    Initialize Vertex AI with CMEK configuration.
    
    Args:
        project_id: GCP project ID
        location: GCP region (e.g., 'us-central1')
        encryption_spec_key_name: Full resource name of the KMS key
                                 (e.g., 'projects/PROJECT_ID/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY')
    
    Example:
        initialize_vertex_with_cmek(
            project_id='my-healthcare-project',
            location='us-central1',
            encryption_spec_key_name='projects/my-healthcare-project/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key'
        )
    """
    aiplatform.init(
        project=project_id,
        location=location,
        encryption_spec_key_name=encryption_spec_key_name,
    )
    print(f"✅ Vertex AI initialized with CMEK: {encryption_spec_key_name}")


def create_cmek_training_job(
    project_id: str,
    location: str,
    encryption_spec_key_name: str,
    display_name: str,
    container_uri: str,
    model_serving_container_image_uri: str,
    dataset_id: Optional[str] = None,
    machine_type: str = "n1-standard-4",
    replica_count: int = 1,
) -> aiplatform.Model:
    """
    Create and run a Vertex AI custom training job with CMEK.
    
    All artifacts (model, logs, metadata) are encrypted with the provided key.
    
    Args:
        project_id: GCP project ID
        location: GCP region
        encryption_spec_key_name: Full resource name of the KMS key
        display_name: Display name for the training job
        container_uri: Docker image URI for training (e.g., 'gcr.io/project/training-image:latest')
        model_serving_container_image_uri: Docker image URI for serving
        dataset_id: Optional dataset ID for training
        machine_type: Machine type for training (default: n1-standard-4)
        replica_count: Number of training replicas
    
    Returns:
        Trained model object
    """
    # Initialize with CMEK
    initialize_vertex_with_cmek(project_id, location, encryption_spec_key_name)
    
    # Create custom training job
    job = aiplatform.CustomTrainingJob(
        display_name=display_name,
        container_uri=container_uri,
        model_serving_container_image_uri=model_serving_container_image_uri,
        # Ensure training artifacts use CMEK
        encryption_spec_key_name=encryption_spec_key_name,
    )
    
    print(f"🚀 Starting CMEK-encrypted training job: {display_name}")
    
    # Run the training job
    model = job.run(
        machine_type=machine_type,
        replica_count=replica_count,
        model_display_name=f"{display_name}-model",
        # Model registry artifacts also encrypted
        encryption_spec_key_name=encryption_spec_key_name,
    )
    
    print(f"✅ Training complete. Model: {model.resource_name}")
    return model


def deploy_cmek_endpoint(
    model: aiplatform.Model,
    endpoint_display_name: str,
    encryption_spec_key_name: str,
    machine_type: str = "n1-standard-4",
    min_replica_count: int = 1,
    max_replica_count: int = 10,
) -> aiplatform.Endpoint:
    """
    Deploy a CMEK-encrypted model to a Vertex AI endpoint.
    
    Prediction endpoint artifacts are also encrypted.
    
    Args:
        model: Trained model object
        endpoint_display_name: Display name for the endpoint
        encryption_spec_key_name: Full resource name of the KMS key
        machine_type: Machine type for predictions
        min_replica_count: Minimum number of replicas
        max_replica_count: Maximum number of replicas
    
    Returns:
        Deployed endpoint object
    """
    print(f"🚀 Deploying CMEK-encrypted endpoint: {endpoint_display_name}")
    
    endpoint = model.deploy(
        deployed_model_display_name=endpoint_display_name,
        machine_type=machine_type,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
        # Prediction endpoint artifacts encrypted
        encryption_spec_key_name=encryption_spec_key_name,
    )
    
    print(f"✅ Endpoint deployed: {endpoint.resource_name}")
    return endpoint


def make_prediction_with_cmek(
    endpoint: aiplatform.Endpoint,
    instances: list,
) -> dict:
    """
    Make predictions using a CMEK-encrypted endpoint.
    
    Args:
        endpoint: Deployed endpoint object
        instances: List of prediction instances
    
    Returns:
        Prediction response
    """
    print(f"📊 Making predictions on CMEK-encrypted endpoint...")
    
    response = endpoint.predict(instances=instances)
    
    print(f"✅ Predictions complete. Predictions: {response.predictions}")
    return response


def healthcare_compliance_example():
    """
    Complete example: Healthcare ML pipeline with CMEK
    
    This example demonstrates:
    1. CMEK initialization
    2. Training a diagnostic model with encrypted artifacts
    3. Deploying to an encrypted endpoint
    4. Making predictions with full encryption
    
    All data stays encrypted at rest using customer-managed keys.
    """
    
    # Configuration
    PROJECT_ID = "my-healthcare-project"
    LOCATION = "us-central1"
    ENCRYPTION_KEY = "projects/my-healthcare-project/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key"
    
    # Step 1: Initialize Vertex AI with CMEK
    print("=" * 60)
    print("STEP 1: Initialize Vertex AI with CMEK")
    print("=" * 60)
    initialize_vertex_with_cmek(PROJECT_ID, LOCATION, ENCRYPTION_KEY)
    
    # Step 2: Create and run training job
    print("\n" + "=" * 60)
    print("STEP 2: Create CMEK-encrypted training job")
    print("=" * 60)
    model = create_cmek_training_job(
        project_id=PROJECT_ID,
        location=LOCATION,
        encryption_spec_key_name=ENCRYPTION_KEY,
        display_name="hipaa-compliant-diagnostic-model",
        container_uri="gcr.io/my-healthcare-project/training-image:latest",
        model_serving_container_image_uri="gcr.io/my-healthcare-project/serving-image:latest",
        machine_type="n1-standard-4",
        replica_count=1,
    )
    
    # Step 3: Deploy to CMEK-encrypted endpoint
    print("\n" + "=" * 60)
    print("STEP 3: Deploy to CMEK-encrypted endpoint")
    print("=" * 60)
    endpoint = deploy_cmek_endpoint(
        model=model,
        endpoint_display_name="diagnostic-endpoint",
        encryption_spec_key_name=ENCRYPTION_KEY,
        machine_type="n1-standard-4",
        min_replica_count=1,
        max_replica_count=5,
    )
    
    # Step 4: Make predictions
    print("\n" + "=" * 60)
    print("STEP 4: Make predictions with CMEK encryption")
    print("=" * 60)
    sample_instances = [
        {
            "feature_1": 1.0,
            "feature_2": 2.0,
            "feature_3": 3.0,
        }
    ]
    predictions = make_prediction_with_cmek(endpoint, sample_instances)
    
    print("\n" + "=" * 60)
    print("✅ HEALTHCARE COMPLIANCE PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Model: {model.resource_name}")
    print(f"Endpoint: {endpoint.resource_name}")
    print(f"Encryption Key: {ENCRYPTION_KEY}")
    print("\n💡 All artifacts encrypted at rest with customer-managed keys")
    print("💡 Full audit trail available in Cloud Audit Logs")


if __name__ == "__main__":
    # Run the healthcare compliance example
    healthcare_compliance_example()
