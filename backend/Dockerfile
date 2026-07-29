# Production Dockerfile for ResearchPilot Backend API (CPU-Only ML Stack)
FROM python:3.12-slim

# Set environment variables for Python optimization, non-interactive builds, and CUDA suppression
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    CUDA_VISIBLE_DEVICES=""

WORKDIR /app

# Install minimal Linux system dependencies required by PyMuPDF (fitz), FAISS (OpenMP), and healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for efficient Docker layer caching
COPY requirements.txt .

# 1. Pre-install lightweight CPU-only PyTorch from official PyTorch CPU extra-index URL to prevent CUDA (~2.5GB) bloat
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install remaining backend requirements
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Ensure uploads/ and storage/faiss directories exist
RUN mkdir -p uploads storage/faiss

# Expose API port 8000
EXPOSE 8000

# Container Healthcheck using Python urllib to verify /api/v1/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

# Start the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
