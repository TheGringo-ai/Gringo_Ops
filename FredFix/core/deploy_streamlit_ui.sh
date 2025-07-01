#!/bin/bash
# Deploy Streamlit FredFix UI to Google Cloud Run
# Usage: ./deploy_streamlit_ui.sh <PROJECT_ID> <REGION> <SERVICE_NAME>

set -e

PROJECT_ID=${1:-$(gcloud config get-value project)}
REGION=${2:-us-central1}
SERVICE_NAME=${3:-fredfix-streamlit-ui}
IMAGE=gcr.io/$PROJECT_ID/$SERVICE_NAME:latest

# Build Docker image
echo "Building Docker image..."
docker build -f Dockerfile.streamlit -t $IMAGE .

echo "Pushing image to Google Container Registry..."
docker push $IMAGE

echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image $IMAGE \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8501

echo "Deployment complete!"
echo "Visit your Streamlit UI at:"
gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)'
