# =========================================================
# Label QC Checker Pro
# Dockerfile
# Version 6.1
# =========================================================

# ---------------------------------------------------------
# Base Image
# ---------------------------------------------------------

FROM python:3.11-slim

# ---------------------------------------------------------
# Environment Variables
# ---------------------------------------------------------

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

# ---------------------------------------------------------
# Working Directory
# ---------------------------------------------------------

WORKDIR /app

# ---------------------------------------------------------
# Install System Packages
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# Copy Requirements
# ---------------------------------------------------------

COPY requirements.txt .

# ---------------------------------------------------------
# Upgrade pip
# ---------------------------------------------------------

RUN python -m pip install --upgrade pip setuptools wheel

# ---------------------------------------------------------
# Install Python Packages
# ---------------------------------------------------------

RUN pip install -r requirements.txt

# ---------------------------------------------------------
# Copy Project Files
# ---------------------------------------------------------

COPY . .

# ---------------------------------------------------------
# Create Required Directories
# ---------------------------------------------------------

RUN mkdir -p \
    uploads \
    reports \
    temp

# ---------------------------------------------------------
# Expose Application Port
# ---------------------------------------------------------

EXPOSE 5000

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------

HEALTHCHECK --interval=30s \
            --timeout=10s \
            --start-period=30s \
            --retries=3 \
CMD curl --fail http://localhost:5000/health || exit 1

# ---------------------------------------------------------
# Start Application
# ---------------------------------------------------------

CMD gunicorn \
    --workers 2 \
    --threads 2 \
    --timeout 300 \
    --bind 0.0.0.0:5000 \
    app:app