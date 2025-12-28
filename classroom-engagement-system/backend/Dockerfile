# syntax=docker/dockerfile:1.4

FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies (cache pip downloads with BuildKit)
RUN --mount=type=cache,id=pycache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
