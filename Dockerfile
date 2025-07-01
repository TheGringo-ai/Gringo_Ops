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
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# Copy project definition and source code
COPY pyproject.toml ./
COPY . .

# Install the project and its dependencies using pyproject.toml
RUN pip install --upgrade pip && pip install .

# Expose the port Cloud Run will use
EXPOSE 8080

# Launch the LineSmart Technician Hub (the unified-dashboard)
CMD ["python", "-m", "streamlit", "run", "GringoOpsHub/config.py", "--server.port=8080", "--server.enableCORS=false"]