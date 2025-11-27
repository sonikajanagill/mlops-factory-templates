#!/bin/bash
# setup_aws_wif.sh
# Phase 1: GCP Configuration (The Trust Side)

set -e

export PROJECT_ID="your-ml-project"
export POOL_ID="aws-prod-pool"
export LOCATION="global"
export PROVIDER_ID="aws-provider"
export AWS_ACCOUNT_ID="123456789012"  # Replace with your AWS Account ID
export SA_NAME="vertex-training-sa"

echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create $POOL_ID \
  --project=$PROJECT_ID \
  --location=$LOCATION \
  --display-name="AWS Production ML Workloads" \
  --description="Federated access for AWS-based ML pipelines"

echo "Creating AWS Provider..."
gcloud iam workload-identity-pools providers create-aws $PROVIDER_ID \
  --project=$PROJECT_ID \
  --location=$LOCATION \
  --workload-identity-pool=$POOL_ID \
  --account-id=$AWS_ACCOUNT_ID

echo "Creating Service Account..."
gcloud iam service-accounts create $SA_NAME \
  --project=$PROJECT_ID \
  --display-name="Vertex AI Training Agent"

echo "Granting permissions..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

echo "Binding the Trust..."
POOL_RESOURCE_NAME=$(gcloud iam workload-identity-pools describe $POOL_ID \
  --project=$PROJECT_ID --location=$LOCATION --format="value(name)")

gcloud iam service-accounts add-iam-policy-binding \
  "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/$POOL_RESOURCE_NAME/attribute.aws_role/arn:aws:iam::$AWS_ACCOUNT_ID:role/ml-training-role"

echo "Setup complete!"
