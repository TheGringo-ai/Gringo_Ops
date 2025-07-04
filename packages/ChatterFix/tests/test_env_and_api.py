import os
import pytest
import requests

def test_fredfix_api_env():
    assert os.getenv("FREDFIX_API_URL"), "FREDFIX_API_URL not set"
    assert os.getenv("FRED_FIX_API_KEY"), "FRED_FIX_API_KEY not set"

def test_fredfix_api_response():
    url = os.getenv("FREDFIX_API_URL")
    key = os.getenv("FRED_FIX_API_KEY")
    if not url or not key:
        pytest.skip("API env not set")
    payload = {"command": "ping", "model": "openai"}
    resp = requests.post(f"{url}/run", json=payload, headers={"x-api-key": key}, timeout=30)
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data
