# Use an official Python runtime as base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

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

RUN apt-get update && apt-get install -y \
    gnupg \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libxss1 \
    libxtst6 \
    libgbm1 \
    libgtk-3-0 \
    libxshmfence-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade webdriver-manager
# Add this to install Google Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
    > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade setuptools wheel \
    && pip install --no-cache-dir --use-pep517 -r requirements.txt

RUN python download_models.py

# Expose port
EXPOSE 8000

# Start the Flask app
# CMD ["python", "main.py"]

# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "--timeout", "120", "main:app"]
