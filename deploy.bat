@echo off
REM GCP Cloud Run Deployment Script for AI Video Generator (Windows)

set PROJECT_ID=aivideogenerator-482415
set REGION=asia-south1
set SERVICE_NAME=adura-ai

echo Starting deployment of AI Video Generator to GCP Cloud Run...

REM Check if gcloud is installed
where gcloud >nul 2>&1
if errorlevel 1 (
    echo Error: gcloud CLI is not installed or not in PATH
    echo Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install
    echo After installation, restart your command prompt or PowerShell
    pause
    exit /b 1
)

REM Get Project ID from user if not set
if "%PROJECT_ID%"=="" (
    set /p PROJECT_ID="Enter your GCP Project ID: "
    if "%PROJECT_ID%"=="" (
        echo Error: Project ID is required
        pause
        exit /b 1
    )
)

echo Project ID: %PROJECT_ID%
echo Region: %REGION%

REM Set the project
echo Setting GCP project...
gcloud config set project %PROJECT_ID%

REM Deploy to Cloud Run using --source flag to build and deploy in one step
echo Deploying to Cloud Run from source...
gcloud run deploy %SERVICE_NAME% ^
    --source . ^
    --platform managed ^
    --region %REGION% ^
    --port 8080 ^
    --memory 2Gi ^
    --cpu 2 ^
    --timeout 300s ^
    --max-instances 10 ^
    --allow-unauthenticated ^
    --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest

echo.
echo Deployment completed!
echo Your service is available at:
gcloud run services list --platform managed --region %REGION% --format="value(status.url)" --filter="metadata.name=%SERVICE_NAME%"

echo.
echo Press any key to continue...
pause >nul