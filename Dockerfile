# Use Python base image
FROM python:3.11-slim

# Install system dependencies (Java for LanguageTool, FFmpeg for audio, and GLib/OpenCV requisites)
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-jre-headless \
    ffmpeg \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY backend/ ./backend/

# Setup path
ENV PYTHONPATH="/app/backend"

# Start FastAPI server, binding to the port assigned by Render
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
