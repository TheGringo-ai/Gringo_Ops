# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Set the Python path to include the app directory, allowing for absolute imports
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copy the requirements file into the container at /app
COPY requirements.txt /app/requirements.txt

# Install system dependencies for tesseract
RUN apt-get update && apt-get install -y tesseract-ocr

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY . /app

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint script as the container's entrypoint.
ENTRYPOINT ["/app/entrypoint.sh"]
