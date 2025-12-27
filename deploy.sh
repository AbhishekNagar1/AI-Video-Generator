#!/bin/bash

# GCP Cloud Run Deployment Script for AI Video Generator

# Set your GCP project ID
PROJECT_ID="aivideogenerator-482415"  # Replace with your actual project ID
REGION="asia-south1"  # You can change this to your preferred region

# Check if PROJECT_ID is set
if [ -z "$PROJECT_ID" ]; then
    echo "Error: PROJECT_ID is not set in deploy.sh"
    echo "Please edit this script and set PROJECT_ID to your GCP project ID"
    exit 1
fi

# Set the service name
SERVICE_NAME="adura-ai"

echo "Starting deployment of AI Video Generator to GCP Cloud Run..."
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"

# Authenticate with Google Cloud (uncomment if needed)
# gcloud auth login

# Set the project
gcloud config set project $PROJECT_ID

# Deploy to Cloud Run using --source flag to build and deploy in one step
echo "Building and deploying from source..."
gcloud run deploy $SERVICE_NAME \
    --source . \
    --platform managed \
    --region $REGION \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300s \
    --max-instances 10 \
    --allow-unauthenticated \
    --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest

echo "Deployment completed!"
echo "Your service is available at:"
gcloud run services list --platform managed --region $REGION --format="value(status.url)" --filter="metadata.name=$SERVICE_NAME"