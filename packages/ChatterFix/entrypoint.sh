#!/bin/sh
# This script ensures that the application starts in a controlled and predictable way.

# Exit immediately if a command exits with a non-zero status.
set -e
# Print each command to stdout before executing it.
set -x

# 1. Run the pre-flight check for Firebase initialization.
# The main.py script will exit with 0 on success or 1 on failure.
# We run this in the foreground to ensure it completes successfully before starting the app.
set +x # Temporarily turn off command printing to avoid leaking secrets
echo "--- Running pre-flight initialization check ---"
python -u main.py
set -x # Turn command printing back on

# 2. Start the Streamlit application.
# The PORT environment variable is automatically provided by Cloud Run.
echo "--- Starting Streamlit application ---"
streamlit run frontend/dashboard.py --server.port=${PORT} --server.address=0.0.0.0 --server.headless=true

