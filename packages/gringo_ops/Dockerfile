# Use the official Python slim image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy full project (excluding ignored files)
COPY . .

# Expose Streamlit port
EXPOSE 8080

# Launch FredFix Streamlit UI app (optimized for Cloud Run, uses $PORT)
CMD ["sh", "-c", "streamlit run ChatterFix/pages/8_FredFix_Agent.py --server.port=$PORT --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false"]