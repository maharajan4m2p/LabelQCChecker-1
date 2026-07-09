# =========================================================
# Label QC Checker Pro
# Dockerfile
# =========================================================

# Base Image
FROM python:3.11-slim

# Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# Working Directory
WORKDIR /app

# Install System Dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    curl \
    wget \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libzbar0 \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create required folders
RUN mkdir -p uploads reports temp

# Expose port
EXPOSE 5000

# Expose port
EXPOSE 5000

# Health Check
HEALTHCHECK CMD curl --fail http://localhost:5000/health || exit 1

# Start Gunicorn
CMD ["gunicorn", "--workers", "1", "--threads", "1", "--preload", "--timeout", "300", "--bind", "0.0.0.0:5000", "app:app"]