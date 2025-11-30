#!/bin/bash
# setup_cmek.sh
# Complete CMEK setup for Vertex AI healthcare workloads

set -e

export PROJECT_ID="${1:-my-healthcare-project}"
export LOCATION="${2:-us-central1}"
export KEYRING_NAME="${3:-healthcare-ml-keyring}"
export KEY_NAME="${4:-vertex-artifacts-key}"

echo "=========================================="
echo "CMEK Setup for Vertex AI"
echo "=========================================="
echo "Project ID: $PROJECT_ID"
echo "Location: $LOCATION"
echo "Key Ring: $KEYRING_NAME"
echo "Key Name: $KEY_NAME"
echo ""

# Step 1: Create KMS Key Ring
echo "Step 1: Creating KMS Key Ring..."
gcloud kms keyrings create "$KEYRING_NAME" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" || echo "Key ring already exists"

# Step 2: Create Encryption Key
echo "Step 2: Creating Encryption Key..."
gcloud kms keys create "$KEY_NAME" \
  --keyring="$KEYRING_NAME" \
  --location="$LOCATION" \
  --purpose=encryption \
  --rotation-period=7776000s \
  --next-rotation-time=$(date -u -d "+90 days" +%Y-%m-%dT%H:%M:%SZ) \
  --project="$PROJECT_ID" || echo "Key already exists"

# Step 3: Get Vertex AI Service Account
echo "Step 3: Getting Vertex AI Service Account..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
VERTEX_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com"
echo "Vertex AI Service Account: $VERTEX_SA"

# Step 4: Grant Permissions
echo "Step 4: Granting CMEK permissions to Vertex AI..."
gcloud kms keys add-iam-policy-binding "$KEY_NAME" \
  --keyring="$KEYRING_NAME" \
  --location="$LOCATION" \
  --member="serviceAccount:${VERTEX_SA}" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter" \
  --project="$PROJECT_ID"

# Step 5: Output Encryption Key Name
echo ""
echo "=========================================="
echo "✅ CMEK Setup Complete!"
echo "=========================================="
ENCRYPTION_KEY="projects/${PROJECT_ID}/locations/${LOCATION}/keyRings/${KEYRING_NAME}/cryptoKeys/${KEY_NAME}"
echo "Encryption Key Name:"
echo "$ENCRYPTION_KEY"
echo ""
echo "Use this in your Vertex AI initialization:"
echo "aiplatform.init("
echo "    project='$PROJECT_ID',"
echo "    location='$LOCATION',"
echo "    encryption_spec_key_name='$ENCRYPTION_KEY'"
echo ")"
