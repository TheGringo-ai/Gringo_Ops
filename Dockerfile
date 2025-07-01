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

# Copy requirements files
COPY requirements.txt ./
COPY Gringo_Ops/ChatterFix/requirements.txt ./Gringo_Ops/ChatterFix/requirements.txt
COPY GringoOpsHub/requirements.txt ./GringoOpsHub/requirements.txt
COPY pyproject.toml ./
COPY . .

# Install build dependencies and all requirements
RUN pip install --upgrade pip setuptools wheel cython \
    && if [ -f requirements.txt ]; then pip install -r requirements.txt; fi \
    && if [ -f Gringo_Ops/ChatterFix/requirements.txt ]; then pip install -r Gringo_Ops/ChatterFix/requirements.txt; fi \
    && if [ -f GringoOpsHub/requirements.txt ]; then pip install -r GringoOpsHub/requirements.txt; fi \
    && pip install .

# Expose the port Cloud Run will use
EXPOSE 8080

# Launch ChatterFix (adjust the path if your main file is different)
CMD ["python", "-m", "streamlit", "run", "Gringo_Ops/ChatterFix/app.py", "--server.port=8080", "--server.enableCORS=false"]