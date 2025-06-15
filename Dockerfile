# Use the official Python slim image
FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    PATH="/app/.venv/bin:$PATH"

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ethtool \
    linux-headers \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment, install dependencies
COPY requirements.txt .
RUN python -m venv .venv \
    && . .venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install black pytest rich

# Copy full project (excluding ignored files)
COPY . .

# Expose Streamlit port
EXPOSE 8080

# Launch Streamlit app
CMD ["streamlit", "run", "FredFix/fredfix_ui.py", "--server.port=8080", "--server.enableCORS=false"]