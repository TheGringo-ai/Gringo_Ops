#!/bin/bash
# Usage: ./deploy_cloudrun.sh <GCP_PROJECT_ID> <REGION>
set -e
PROJECT_ID=${1:-YOUR_PROJECT_ID}
REGION=${2:-us-central1}
SERVICE_NAME=fredfix-agent
IMAGE=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

cd "$(dirname "$0")"

echo "Building Docker image..."
gcloud builds submit --tag $IMAGE .

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated

echo "Done! Visit the Cloud Run console to set OPENAI_API_KEY as an environment variable."
