# Infrastructure as Code (Terraform)

This directory contains the Terraform configuration to deploy the MLOps Factory infrastructure.

## Modules

### Core Infrastructure

* **project-setup**: Enables required Google Cloud APIs.
* **storage**: Creates GCS buckets for data and artifacts.
* **monitoring**: Configures Alert Policies and Notification Channels.

### Identity & Access Management

* **iam**: Creates Service Accounts with least-privilege roles.
  * `sa-composer`: For Cloud Composer environment.
  * `sa-dataproc`: For Dataproc Serverless jobs.
  * `sa-vertex-pipeline`: For Vertex AI Pipelines.

### Orchestration & ML

* **composer**: Deploys Cloud Composer 3 environment.
* **vertex-ai**: Sets up Feature Store and Artifact Registry.

### Multi-Cloud Security

* **wif_aws**: Configures Workload Identity Federation for AWS.
  * Workload Identity Pool for AWS identities
  * AWS Provider for token exchange
  * Service Account impersonation bindings
  * Zero static credentials authentication
* **wif_azure**: Configures Workload Identity Federation for Azure.
  * Workload Identity Pool for Azure identities
  * OIDC Provider for Azure token exchange
  * Managed Identity integration

### Compliance & Encryption

* **cmek**: Customer Managed Encryption Keys for Vertex AI.
  * KMS Key Ring and encryption keys
  * 90-day key rotation
  * Optional separate keys for anonymized features
  * IAM bindings for Vertex AI service accounts
  * Audit logging for compliance
  * Healthcare/HIPAA-compliant artifact encryption

## Usage

### Basic Deployment

```bash
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID"
terraform apply -var="project_id=YOUR_PROJECT_ID"
```

### Deploy Specific Modules

```bash
# Deploy only WIF for AWS
terraform apply -target=module.wif_aws -var="project_id=YOUR_PROJECT_ID"

# Deploy only CMEK
terraform apply -target=module.cmek -var="project_id=YOUR_PROJECT_ID"

# Deploy only Vertex AI
terraform apply -target=module.vertex_ai -var="project_id=YOUR_PROJECT_ID"
```

### CMEK Setup Example

```bash
terraform apply \
  -var="project_id=my-healthcare-project" \
  -var="kms_location=us-central1" \
  -var="create_separate_anonymized_key=true" \
  -target=module.cmek
```

## Module Details

### WIF (Workload Identity Federation)

**AWS Integration** (`wif_aws`):

* Enables keyless authentication from AWS to Vertex AI
* Creates federated trust between AWS roles and GCP service accounts
* Supports attribute-based access control (ABAC)
* Zero static credentials required

**Azure Integration** (`wif_azure`):

* Enables keyless authentication from Azure to Vertex AI
* Uses OpenID Connect (OIDC) for token exchange
* Integrates with Azure Managed Identity
* Compliance-ready for regulated workloads

### CMEK (Customer Managed Encryption Keys)

Provides encryption at rest for all Vertex AI artifacts:

* **Training artifacts**: Models, checkpoints, logs
* **Model registry**: Stored models and metadata
* **Prediction endpoints**: Endpoint artifacts and predictions
* **Compliance**: Full audit trail in Cloud Audit Logs

**Key Features**:

* 90-day automatic key rotation
* Optional separate keys for different sensitivity levels
* Audit logging enabled by default
* Healthcare/HIPAA compliance support

**Usage in Python**:

```python
from google.cloud import aiplatform

aiplatform.init(
    project='my-healthcare-project',
    location='us-central1',
    encryption_spec_key_name='projects/PROJECT_ID/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key'
)
```
