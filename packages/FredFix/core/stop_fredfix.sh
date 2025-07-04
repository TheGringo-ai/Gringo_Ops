#!/bin/bash
# Stop all running uvicorn dev servers for FredFix
pkill -f "uvicorn.*Fred_Fix_agent:app"
echo "Stopped all FredFix dev servers."
