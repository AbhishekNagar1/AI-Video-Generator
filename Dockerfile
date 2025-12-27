FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# System dependencies (IMPORTANT for Pillow)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libgl1 \
    libglib2.0-0 \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Correct requirements path
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Set working directory to backend
WORKDIR /app/backend

# Runtime folders
RUN mkdir -p data/output data/videos data/audio data/presentations data/temp ../logs

EXPOSE 8080

# Run the application from the backend directory
CMD exec gunicorn --bind :$PORT --workers 1 --timeout 120 --keep-alive 10 --access-logfile - --error-logfile - app:app