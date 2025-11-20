# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    portaudio19-dev \
    build-essential \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/ ./services/
COPY *.py .

# Create directories for models and audio files
RUN mkdir -p models models/.cache

# Expose port for FastAPI
EXPOSE 8000

# Run the web voice agent
CMD ["python", "web_app.py"]
