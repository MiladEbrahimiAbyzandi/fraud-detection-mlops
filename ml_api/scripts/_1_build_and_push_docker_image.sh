#!/bin/bash
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Running $SCRIPT_NAME"
echo "Script directory: $SCRIPT_DIR"

GCP_PROJECT_ID=data-461916
GCP_REGION=us-central1

echo "📦 Creating artifact repository for docker images if it doesn't exist..."
if ! gcloud artifacts repositories describe "$GCP_PROJECT_ID" \
  --location="$GCP_REGION" \
  --project="$GCP_PROJECT_ID" > /dev/null 2>&1; then

  gcloud artifacts repositories create "$GCP_PROJECT_ID" \
    --repository-format=docker \
    --location="$GCP_REGION" \
    --project="$GCP_PROJECT_ID"
fi


echo "🐳 Configuring docker to use the artifact repository..."
gcloud auth configure-docker $GCP_REGION-docker.pkg.dev --project=$GCP_PROJECT_ID


# TODO 
- build the docker image
- tag the docker image
- push the docker image to the artifact repository
- deploy the docker image to Cloud Run
