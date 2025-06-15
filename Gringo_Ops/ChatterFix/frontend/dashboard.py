import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './FredFix')))
name: Deploy to Google Cloud Run

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Authenticate with Google Cloud
      uses: google-github-actions/auth@v1
      with:
        credentials_json: ${{ secrets.GCP_SA_KEY }}

    - name: Set up Google Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: unified-dashboard
        install_components: 'gcloud'

    - name: Deploy to Cloud Run
      run: |
        gcloud run deploy unified-dashboard \
          --source . \
          --region us-central1 \
          --platform managed \
          --allow-unauthenticated \
          --project unified-dashboard

    - name: Confirm Deployment
      run: |
        echo "✅ Deployment triggered. Verifying service status..."
        sleep 10
        curl --fail --silent --show-error https://unified-dashboard-<your-subdomain>-uc.a.run.app || echo "⚠️ Service ping failed. Check deployment logs."

    - name: Auto-commit memory logs
      run: |
        if [ -f memory/log.txt ]; then
          git config user.name "FredFix Auto"
          git config user.email "bot@fredfix.io"
          git add memory/log.txt
          git commit -m "🧠 Memory log auto-commit post deploy"
          git push origin main || echo "⚠️ Could not push memory logs."
        fi