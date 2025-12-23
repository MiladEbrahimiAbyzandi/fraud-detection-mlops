#!/bin/bash
SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

echo "Running $SCRIPT_NAME"
echo "Script directory: $SCRIPT_DIR"
echo "Base directory: $BASE_DIR"


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


# Build the docker image
echo "Building the Docker image"
docker build -t $APP_NAME:latest -f $BASE_DIR/Dockerfile $BASE_DIR

echo "Tag Docker image for push to artifact repository" 
docker tag $APP_NAME:latest $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_PROJECT_ID/$APP_NAME:latest

echo "Push Docker image to artifact repository"
docker push $GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_PROJECT_ID/$APP_NAME:latest
# TODO 
# - build the docker image
# - tag the docker image
# - push the docker image to the artifact repository
# - deploy the docker image to Cloud Run
echo "🚀 Deploying Docker image to Cloud Run..."
gcloud run deploy $APP_NAME \
  --image=$GCP_REGION-docker.pkg.dev/$GCP_PROJECT_ID/$GCP_PROJECT_ID/$APP_NAME:latest \
  --region=$GCP_REGION \
  --project=$GCP_PROJECT_ID \
  --min-instances=0 \
  --max-instances=2 \
  --port=80 \
  --env-vars-file=$SCRIPT_DIR/cloudrun.env \
  --allow-unauthenticated

echo "✅ Deployment complete!"