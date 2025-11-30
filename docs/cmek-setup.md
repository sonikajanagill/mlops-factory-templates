# CMEK Setup for Vertex AI (Healthcare & Compliance)

Complete implementation of Customer Managed Encryption Keys (CMEK) for Vertex AI workloads. This guide covers production-ready Terraform modules and Python examples for healthcare, HIPAA, and compliance-regulated ML pipelines.

## 🔐 Why CMEK Matters for Healthcare

For healthcare and regulated workloads, CMEK provides:

- **Regulatory Control**: Prove to auditors you control encryption keys, not Google
- **Key Rotation**: Automatic 90-day rotation meets compliance requirements
- **Revocation Power**: Instantly revoke access to all ML artifacts by disabling the key
- **Audit Trail**: Every key usage logged in Cloud Audit Logs for compliance reporting
- **Data Residency**: Keys stay in your region; data never leaves encrypted state

## 🚀 Quick Start

### Prerequisites

- GCP project with Vertex AI enabled
- Terraform >= 1.0
- `gcloud` CLI configured
- Python 3.9+

### Step 1: Deploy CMEK Infrastructure with Terraform

```bash
cd terraform/modules/cmek

# Initialize Terraform
terraform init

# Create terraform.tfvars with your configuration
cat > terraform.tfvars << EOF
project_id                    = "my-healthcare-project"
kms_location                  = "us-central1"
keyring_name                  = "healthcare-ml-keyring"
crypto_key_name               = "vertex-artifacts-key"
create_separate_anonymized_key = true
enable_audit_logging          = true
EOF

# Plan and apply
terraform plan
terraform apply
```

### Step 2: Capture Terraform Outputs

After Terraform completes, capture the encryption key name:

```bash
# Get the encryption spec key name for Python scripts
ENCRYPTION_KEY=$(terraform output -raw encryption_spec_key_name)
echo "Encryption Key: $ENCRYPTION_KEY"
```

### Step 3: Run Python Training Example

```bash
cd src/cmek_training

# Install dependencies
pip install google-cloud-aiplatform google-cloud-storage

# Update the configuration in vertex_cmek_training.py
# Then run the example
python vertex_cmek_training.py
```

## 📊 Terraform Configuration

### Module Location

The CMEK Terraform module is located at: `terraform/modules/cmek/`

### Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `project_id` | - | GCP Project ID (required) |
| `kms_location` | `us-central1` | KMS key ring location |
| `keyring_name` | `healthcare-ml-keyring` | Name of the KMS key ring |
| `crypto_key_name` | `vertex-artifacts-key` | Name of the encryption key |
| `key_rotation_period` | `7776000s` (90 days) | Key rotation period |
| `create_separate_anonymized_key` | `false` | Create separate key for anonymized features |
| `enable_audit_logging` | `true` | Enable KMS audit logging |

### Outputs

```hcl
keyring_id                    # ID of the KMS key ring
keyring_name                  # Full resource name of key ring
vertex_artifacts_key_id       # ID of the encryption key
vertex_artifacts_key_name     # Full resource name of encryption key
encryption_spec_key_name      # Ready-to-use encryption spec for Vertex AI
```

## 🐍 Python Usage

### Basic Initialization

```python
from google.cloud import aiplatform

aiplatform.init(
    project='my-healthcare-project',
    location='us-central1',
    encryption_spec_key_name='projects/PROJECT_ID/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key'
)
```

### Training with CMEK

```python
job = aiplatform.CustomTrainingJob(
    display_name='hipaa-compliant-training',
    container_uri='gcr.io/my-project/training-image:latest',
    model_serving_container_image_uri='gcr.io/my-project/serving-image:latest',
    encryption_spec_key_name='projects/PROJECT_ID/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key'
)

model = job.run(
    machine_type='n1-standard-4',
    replica_count=1,
    model_display_name='diagnostic-model-v1',
    encryption_spec_key_name='projects/PROJECT_ID/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key'
)
```

### Deployment with CMEK

```python
endpoint = model.deploy(
    deployed_model_display_name='diagnostic-endpoint',
    machine_type='n1-standard-4',
    encryption_spec_key_name='projects/PROJECT_ID/locations/us-central1/keyRings/healthcare-ml-keyring/cryptoKeys/vertex-artifacts-key'
)
```

## ✅ Compliance Checklist

Use this checklist to verify your CMEK setup meets compliance requirements:

### Encryption & Key Management

- [ ] KMS key ring created in compliant region
- [ ] Key rotation enabled (90-day rotation recommended)
- [ ] Separate keys for different sensitivity levels (e.g., anonymized vs. PHI)
- [ ] Key access restricted to service accounts only
- [ ] No key material exported or shared

### Access Control

- [ ] Vertex AI service account has `cloudkms.cryptoKeyEncrypterDecrypter` role
- [ ] Custom service accounts explicitly granted permissions
- [ ] No wildcard permissions (`*`) in IAM policies
- [ ] Service account impersonation restricted to specific roles

### Audit & Monitoring

- [ ] Cloud Audit Logs enabled for KMS operations
- [ ] Audit logs retention >= 90 days
- [ ] Monitoring alerts configured for key usage anomalies
- [ ] Regular audit log reviews scheduled

### Data Residency

- [ ] KMS key ring in same region as data
- [ ] VPC Service Controls configured (if required)
- [ ] Cloud Interconnect used for hybrid setups (if required)
- [ ] Data never leaves encrypted state

### Compliance Documentation

- [ ] CMEK architecture documented
- [ ] Key rotation procedures documented
- [ ] Incident response plan for key compromise
- [ ] Compliance evidence collected for auditors

## 🔍 Verification

### Verify Key Creation

```bash
gcloud kms keyrings list --location=us-central1 --project=my-healthcare-project
gcloud kms keys list --keyring=healthcare-ml-keyring --location=us-central1 --project=my-healthcare-project
```

### Verify IAM Bindings

```bash
gcloud kms keys get-iam-policy vertex-artifacts-key \
  --keyring=healthcare-ml-keyring \
  --location=us-central1 \
  --project=my-healthcare-project
```

### Verify Audit Logs

```bash
gcloud logging read "resource.type=k8s_cluster AND protoPayload.methodName=cloudkms.projects.locations.keyRings.cryptoKeys.encrypt" \
  --limit=10 \
  --project=my-healthcare-project
```

## 🛠️ Troubleshooting

### Error: "Permission denied on KMS key"

**Cause**: Vertex AI service account doesn't have permission to use the key.

**Fix**:

```bash
# Get Vertex AI service account
PROJECT_NUMBER=$(gcloud projects describe my-healthcare-project --format='value(projectNumber)')
VERTEX_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com"

# Grant permission
gcloud kms keys add-iam-policy-binding vertex-artifacts-key \
  --keyring=healthcare-ml-keyring \
  --location=us-central1 \
  --member="serviceAccount:${VERTEX_SA}" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
  --project=my-healthcare-project
```

### Error: "Key not found"

**Cause**: Encryption key name format is incorrect.

**Fix**: Use the full resource name format:

```text
projects/PROJECT_ID/locations/LOCATION/keyRings/KEYRING_NAME/cryptoKeys/KEY_NAME
```

### Error: "Encryption spec not supported"

**Cause**: Vertex AI resource doesn't support CMEK in this region.

**Fix**: Verify region support and try a different region (e.g., `us-central1`, `europe-west1`).

## 📚 References

- [Vertex AI CMEK Documentation](https://cloud.google.com/vertex-ai/docs/general/cmek)
- [Cloud KMS Documentation](https://cloud.google.com/kms/docs)
- [HIPAA Compliance on GCP](https://cloud.google.com/security/compliance/hipaa)
- [Article: Implementing Zero-Trust Multi-Cloud Access](../Article5_Multi_cloud_Security_Part2_v2.MD)

## 💡 Best Practices

1. **Key Rotation**: Enable automatic key rotation (90 days recommended)
2. **Separate Keys**: Use different keys for different sensitivity levels
3. **Audit Logging**: Enable and monitor all KMS operations
4. **Least Privilege**: Grant only necessary permissions to service accounts
5. **Documentation**: Keep compliance documentation up to date
6. **Testing**: Test key rotation and recovery procedures regularly
7. **Monitoring**: Set up alerts for unusual key access patterns

## 🤝 Contributing

Found an issue or have a suggestion? Please open an issue or submit a pull request.

## 📄 License

This code is provided as-is for educational and production use.
