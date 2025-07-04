#!/bin/zsh

# Clean compiled Python artifacts
find . -name "__pycache__" -type d -exec rm -r {} +
find . -name "*.pyc" -delete

# Remove local virtual environments
rm -rf .venv venv env

# Delete logs
find . -name "*.log" -delete

# Delete test/type checker caches
rm -rf .pytest_cache .mypy_cache

# Clean build artifacts
rm -rf build dist
find . -name "*.egg-info" -type d -exec rm -rf {} +
find . -name "*.whl" -delete

# Remove VSCode settings
rm -rf .vscode

# Remove notebook junk
find . -name ".ipynb_checkpoints" -type d -exec rm -rf {} +

# Remove Streamlit + sensitive working files
rm -rf .streamlit
rm -f memory.json keys_test.py agent_config.yaml

