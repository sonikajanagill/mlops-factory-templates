#!/bin/bash
# generate_cred_config.sh
# Helper to generate credential-config.json

set -e

export PROJECT_NUMBER="YOUR_PROJECT_NUMBER"
export POOL_ID="aws-prod-pool"
export PROVIDER_ID="aws-provider"
export SA_NAME="vertex-training-sa"
export PROJECT_ID="your-ml-project"

gcloud iam workload-identity-pools create-cred-config \
  projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_ID/providers/$PROVIDER_ID \
  --service-account="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --aws \
  --output-file="credential-config.json"

echo "Generated credential-config.json"
