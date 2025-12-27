# PowerShell Deployment Script for AI Video Generator to GCP Cloud Run

# Set your GCP project ID
$PROJECT_ID = ""  # Replace with your actual project ID
$REGION = "us-central1"  # You can change this to your preferred region
$SERVICE_NAME = "ai-video-generator"

# Check if PROJECT_ID is set
if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "Error: PROJECT_ID is not set in deploy.ps1" -ForegroundColor Red
    Write-Host "Please edit this script and set PROJECT_ID to your GCP project ID" -ForegroundColor Red
    exit 1
}

Write-Host "Starting deployment of AI Video Generator to GCP Cloud Run..." -ForegroundColor Green
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow

# Check if gcloud is installed
try {
    $gcloud_version = gcloud version 2>$null
    if ($gcloud_version) {
        Write-Host "gcloud CLI is installed" -ForegroundColor Green
    }
}
catch {
    Write-Host "Error: gcloud CLI is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}

# Set the project
Write-Host "Setting GCP project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Build and push the Docker image to Google Container Registry
Write-Host "Building Docker image..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME"

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $SERVICE_NAME `
    --image "gcr.io/$PROJECT_ID/$SERVICE_NAME" `
    --platform managed `
    --region $REGION `
    --port 8080 `
    --memory 2Gi `
    --cpu 2 `
    --timeout 300s `
    --max-instances 10 `
    --allow-unauthenticated `
    --set-env-vars "GEMINI_API_KEY=projects/$PROJECT_ID/secrets/GEMINI_API_KEY/versions/latest"

Write-Host "Deployment completed!" -ForegroundColor Green
Write-Host "Your service is available at:" -ForegroundColor Green
gcloud run services list --platform managed --region $REGION --format="value(status.url)" --filter="metadata.name=$SERVICE_NAME"