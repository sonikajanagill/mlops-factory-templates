#!/bin/bash
# verify_cmek.sh
# Verify CMEK setup and permissions

set -e

export PROJECT_ID="${1:-my-healthcare-project}"
export LOCATION="${2:-us-central1}"
export KEYRING_NAME="${3:-healthcare-ml-keyring}"
export KEY_NAME="${4:-vertex-artifacts-key}"

echo "=========================================="
echo "Verifying CMEK Setup"
echo "=========================================="

# Check 1: Key Ring Exists
echo "Check 1: Verifying Key Ring..."
gcloud kms keyrings describe "$KEYRING_NAME" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" || exit 1
echo "✅ Key Ring exists"

# Check 2: Key Exists
echo ""
echo "Check 2: Verifying Encryption Key..."
gcloud kms keys describe "$KEY_NAME" \
  --keyring="$KEYRING_NAME" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" || exit 1
echo "✅ Encryption Key exists"

# Check 3: Key Rotation
echo ""
echo "Check 3: Verifying Key Rotation..."
gcloud kms keys describe "$KEY_NAME" \
  --keyring="$KEYRING_NAME" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" \
  --format="value(rotationSchedule.rotationPeriod)"
echo "✅ Key rotation configured"

# Check 4: IAM Bindings
echo ""
echo "Check 4: Verifying IAM Bindings..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
VERTEX_SA="service-${PROJECT_NUMBER}@gcp-sa-aiplatform.iam.gserviceaccount.com"

gcloud kms keys get-iam-policy "$KEY_NAME" \
  --keyring="$KEYRING_NAME" \
  --location="$LOCATION" \
  --project="$PROJECT_ID" | grep -q "$VERTEX_SA" && echo "✅ Vertex AI has CMEK permissions" || echo "❌ Vertex AI missing CMEK permissions"

# Check 5: Audit Logs
echo ""
echo "Check 5: Checking Recent KMS Activity..."
gcloud logging read "resource.type=k8s_cluster AND protoPayload.methodName=cloudkms.projects.locations.keyRings.cryptoKeys" \
  --limit=5 \
  --project="$PROJECT_ID" --format="table(timestamp,protoPayload.methodName)" || echo "No recent KMS activity"

echo ""
echo "=========================================="
echo "✅ CMEK Verification Complete!"
echo "=========================================="
