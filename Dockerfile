# Use official Python image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# --- Streamlit Entrypoint ---
# To deploy the Streamlit dashboard, uncomment below and comment out the FastAPI CMD if not needed
# EXPOSE 8080
# CMD ["streamlit", "run", "gringoops_dashboard.py", "--server.port=8080", "--server.enableCORS=false"]

# --- FastAPI Entrypoint (default) ---
EXPOSE 8080
CMD ["uvicorn", "FredFix/core/agent_api:app", "--host", "0.0.0.0", "--port", "8080"]
