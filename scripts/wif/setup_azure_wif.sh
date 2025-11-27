#!/bin/bash
# setup_azure_wif.sh
# Implementation Pattern 2: Azure to Vertex AI

set -e

export POOL_ID="azure-health-pool"
export PROVIDER_ID="azure-provider"
export TENANT_ID="YOUR_TENANT_ID"

echo "Creating Azure OIDC Provider..."
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_ID \
  --workload-identity-pool=$POOL_ID \
  --issuer-uri="https://sts.windows.net/$TENANT_ID/" \
  --allowed-audiences="api://AzureADTokenExchange"

echo "Setup complete!"
