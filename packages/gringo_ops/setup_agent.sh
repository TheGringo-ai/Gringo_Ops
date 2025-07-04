#!/bin/bash
# Create tools and base files
mkdir -p tools
touch tools/openai_review.py tools/gemini_query.py tools/hf_runner.py

# Create dispatcher and config
touch agent_cli.py
touch agent_config.yaml

# Ensure FredFix/core exists
mkdir -p FredFix/core
