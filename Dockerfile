# Use an official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    git \
    wget \
    curl \
    unzip \
    build-essential \
    python3-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
# RUN pip install --no-cache-dir --upgrade setuptools wheel \
#     && pip install --no-cache-dir --use-pep517 -r requirements.txt

RUN pip install --upgrade setuptools wheel \
    && pip install --use-pep517 -r requirements.txt

RUN python download_models.py

# Expose port
EXPOSE 8000

# Start the Flask app
# CMD ["python", "main.py"]

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "main:app"]
