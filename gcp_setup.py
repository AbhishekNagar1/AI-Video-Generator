#!/usr/bin/env python3
"""
GCP Setup Script for AI Video Generator
This script helps set up the necessary GCP resources for deployment.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{description}")
    print(f"Running: {cmd}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print("✓ Success")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("AI Video Generator - GCP Setup Script")
    print("="*50)
    
    # Get project ID from user
    project_id = input("Enter your GCP project ID: ").strip()
    if not project_id:
        print("Error: Project ID is required")
        sys.exit(1)
    
    print(f"\nSetting up AI Video Generator for project: {project_id}")
    
    # Add Google Cloud SDK to PATH if it's in the expected location
    gcloud_path = r"D:\Project\Google Cloud\google-cloud-sdk\bin"
    if os.path.exists(gcloud_path):
        os.environ["PATH"] = os.environ["PATH"] + ";" + gcloud_path
        print(f"Added Google Cloud SDK to PATH: {gcloud_path}")
    
    # Set the project
    if not run_command(f"gcloud config set project {project_id}", 
                      "Setting GCP project"):
        sys.exit(1)
    
    # Enable required APIs
    apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com", 
        "containerregistry.googleapis.com",
        "secretmanager.googleapis.com",
        "storage.googleapis.com"
    ]
    
    for api in apis:
        if not run_command(f"gcloud services enable {api}", 
                          f"Enabling {api}"):
            print(f"Warning: Failed to enable {api}, continuing...")
    
    # Create a sample .env file if it doesn't exist
    backend_dir = Path("backend")
    env_dir = backend_dir / "env"
    env_dir.mkdir(exist_ok=True)
    
    env_file = env_dir / ".env"
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write("# GCP Secret Manager will override these values in production\n")
            f.write("GEMINI_API_KEY=your_api_key_here\n")
        print(f"\nCreated sample .env file at {env_file}")
        print("Note: This is only for local development. In GCP, the API key will come from Secret Manager.")
    
    # Create data directories
    data_dirs = [
        backend_dir / "data" / "output",
        backend_dir / "data" / "videos", 
        backend_dir / "data" / "audio",
        backend_dir / "data" / "presentations",
        backend_dir / "data" / "temp",
        backend_dir / "logs"
    ]
    
    for data_dir in data_dirs:
        data_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nCreated required data directories in {backend_dir / 'data'}")
    
    # Instructions for API key setup
    print("\n" + "="*50)
    print("NEXT STEPS:")
    print("="*50)
    print(f"1. Get your Gemini API key from: https://aistudio.google.com/app/apikey")
    print(f"2. Add your API key to GCP Secret Manager:")
    print(f"   echo -n 'YOUR_ACTUAL_API_KEY' | gcloud secrets create GEMINI_API_KEY --data-file=-")
    print(f"3. Update deploy.sh with your project ID: {project_id}")
    print(f"4. Run the deployment: ./deploy.sh or deploy.bat")
    print("="*50)
    
    print("\nSetup completed successfully!")
    print("You can now deploy your AI Video Generator to GCP Cloud Run.")

if __name__ == "__main__":
    main()