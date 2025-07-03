# Use official Python image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

# --- Streamlit Entrypoint ---
# Uncomment the following lines to deploy the Streamlit dashboard
# EXPOSE 8080
# CMD ["streamlit", "run", "gringoops_dashboard.py", "--server.port=8080", "--server.enableCORS=false"]

# --- FastAPI Entrypoint ---
# Uncomment the following lines to deploy a FastAPI app (replace 'your_module:app' as needed)
# EXPOSE 8080
# CMD ["uvicorn", "your_module:app", "--host", "0.0.0.0", "--port", "8080"]

# --- CLI Entrypoint (default) ---
CMD ["python", "run_chatterfix_local.py"]
