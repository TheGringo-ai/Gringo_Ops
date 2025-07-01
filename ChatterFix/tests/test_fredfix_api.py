import pytest
import requests
import os

FREDFIX_API_URL = os.getenv("FREDFIX_API_URL", "https://fredfix-agent-487771372565.us-central1.run.app")
FRED_FIX_API_KEY = os.getenv("FRED_FIX_API_KEY", "test-key")

def test_fredfix_run_endpoint():
    payload = {"command": "Test prompt", "model": "openai"}
    headers = {"x-api-key": FRED_FIX_API_KEY}
    resp = requests.post(f"{FREDFIX_API_URL}/run", json=payload, headers=headers, timeout=30)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
