# AI Video Generator

An AI-powered application that generates educational videos from text topics using Google's Gemini AI.

## Features

- Generate educational content using AI
- Convert content to PowerPoint presentations
- Create voiceovers using text-to-speech
- Combine slides with voiceover to create videos
- Responsive web interface

## Tech Stack

- Backend: Flask, Google Gemini AI, MoviePy
- Frontend: HTML, CSS, JavaScript
- Video Processing: FFmpeg
- Cloud Deployment: Google Cloud Platform, Cloud Run

## Prerequisites for GCP Deployment

Before deploying to Google Cloud Platform, you'll need:

1. **Google Cloud SDK** (gcloud CLI):
   - Download from: https://cloud.google.com/sdk/docs/install
   - For Windows: Download the x86-64 installer and run it
   - Make sure to select "Start Google Cloud SDK Shell" after installation
   - Verify installation: `gcloud --version`

2. **A Google Cloud Project**:
   - Create a project at: https://console.cloud.google.com/
   - Note your Project ID

3. **Billing Account**:
   - Ensure billing is enabled for your project (required for Cloud Run)

## Installing Google Cloud SDK (Windows)

1. **Download the installer**:
   - Go to https://cloud.google.com/sdk/docs/install
   - Download "Windows x86-64" version (about 100MB)

2. **Run the installer**:
   - Double-click the downloaded file
   - Follow the installation wizard
   - Keep default settings unless you have specific requirements

3. **Verify installation**:
   - Open a new Command Prompt or PowerShell window
   - Run: `gcloud --version`
   - You should see version information

4. **Initialize the SDK**:
   - Run: `gcloud init`
   - Follow the prompts to log in and select your project

## Deployment to Google Cloud Platform

### Step 1: Prepare Your Project

1. Clone or navigate to your project directory
2. Make the setup script executable:
   ```bash
   python gcp_setup.py
   ```
   This script will:
   - Prompt for your GCP Project ID
   - Set up required directories
   - Create sample configuration files

### Step 2: Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Step 3: Set up API Keys in Secret Manager

1. Get your Gemini API key from: https://aistudio.google.com/app/apikey
2. Create a secret in Google Secret Manager:
   ```bash
   echo -n "YOUR_GEMINI_API_KEY_HERE" | gcloud secrets create GEMINI_API_KEY --data-file=-
   ```

3. Grant Cloud Run service account access to the secret:
   ```bash
   PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format="value(projectNumber)")
   gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
       --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
       --role='roles/secretmanager.secretAccessor'
   ```

### Step 4: Deploy to Cloud Run

1. Update the `deploy.sh` file with your Project ID:
   ```bash
   # Edit deploy.sh and set PROJECT_ID="your-actual-project-id"
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```
   
   On Windows, you can run:
   ```bash
   bash deploy.sh
   ```
   
   Or use the Windows batch file:
   ```bash
   deploy.bat
   ```

### Alternative: Manual Deployment

If you prefer to deploy manually:

1. **Build the container**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/ai-video-generator
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy ai-video-generator \
       --image gcr.io/YOUR_PROJECT_ID/ai-video-generator \
       --platform managed \
       --region us-central1 \
       --port 8080 \
       --memory 2Gi \
       --cpu 2 \
       --timeout 300s \
       --max-instances 10 \
       --allow-unauthenticated \
       --set-env-vars GEMINI_API_KEY=projects/YOUR_PROJECT_ID/secrets/GEMINI_API_KEY/versions/latest
   ```

### Configuration Notes

- The application is configured to use 2GB memory and 2 CPUs as per project requirements
- Maximum timeout is set to 300 seconds to handle video processing tasks
- The application uses Google Cloud Storage for persistent file storage (configure as needed)
- Environment variables are managed via GCP Secret Manager in production

### Architecture

- **Frontend**: Static files served through the Flask application
- **Backend**: Flask API handling video generation requests
- **AI Services**: Google Gemini API for content generation
- **Storage**: Google Cloud Storage for video output (recommended)
- **Processing**: FFmpeg for video processing

### Scaling Configuration

The application is configured with the following scaling parameters:
- Memory: 2GB
- CPU: 2
- Timeout: 300 seconds
- Max instances: 10

## Local Development

To run the application locally:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

3. Run the application:
   ```bash
   cd backend
   python app.py
   ```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
.
├── backend/           # Flask backend API
├── frontend/         # HTML/CSS/JS frontend
├── env/             # Environment variables
├── data/            # Generated content storage
├── docs/            # Documentation
└── tests/           # Test cases
```

## 🚀 Getting Started

1. Clone the repository
2. Set up environment variables in `env/.env`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server:
   ```bash
   python backend/app.py
   ```

## 🔑 Environment Variables

Create a `.env` file in the `env/` directory with:

```
GEMINI_API_KEY=your_gemini_api_key
GOOGLE_TTS_KEY=your_tts_key
```

## 📝 License

MIT License - feel free to use this project for educational purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
