# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY ../../../../requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy FredFix core code
COPY . .

# Set environment variables (customize as needed)
ENV PYTHONUNBUFFERED=1

# Default command (customize as needed)
CMD ["python", "main.py"]