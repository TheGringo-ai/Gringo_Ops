# Dockerfile for ChatterFix Backend
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy only the backend code into the container
COPY ./backend /app/backend

# Install backend dependencies
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Expose the port that the app will run on
EXPOSE 8080

# Command to run the FastAPI application with Gunicorn
# Gunicorn is a production-ready WSGI server
# The app will be served on 0.0.0.0 with the port set by the $PORT environment variable, which is standard for Cloud Run.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "backend.app:app", "--bind", "0.0.0.0:$PORT"]
