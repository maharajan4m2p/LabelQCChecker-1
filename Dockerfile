# ============================================================
# Dockerfile — LabelQCChecker
# ============================================================

# Use Python slim base
FROM python:3.10-slim

# ── Install system dependencies + Tesseract ────────────────
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-ces \
    tesseract-ocr-slk \
    tesseract-ocr-hun \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    tesseract-ocr-ita \
    tesseract-ocr-por \
    tesseract-ocr-pol \
    tesseract-ocr-nld \
    tesseract-ocr-swe \
    tesseract-ocr-nor \
    tesseract-ocr-dan \
    tesseract-ocr-fin \
    tesseract-ocr-ron \
    tesseract-ocr-bul \
    tesseract-ocr-hrv \
    tesseract-ocr-rus \
    tesseract-ocr-ara \
    tesseract-ocr-hin \
    tesseract-ocr-chi-sim \
    tesseract-ocr-jpn \
    tesseract-ocr-kor \
    tesseract-ocr-tur \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# ── Set working directory ──────────────────────────────────
WORKDIR /app

# ── Copy and install Python dependencies ──────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy all project files ─────────────────────────────────
COPY . .

# ── Create uploads folder ──────────────────────────────────
RUN mkdir -p uploads

# ── Expose port ────────────────────────────────────────────
EXPOSE 5000

# ── Start server ───────────────────────────────────────────
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--timeout", "120", \
     "--workers", "1", \
     "--threads", "2", \
     "--log-level", "info", \
     "app:app"]