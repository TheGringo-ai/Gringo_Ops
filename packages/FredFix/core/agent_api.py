from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import sys
import pathlib

# Ensure the parent directory is in sys.path for import
sys.path.append(str(pathlib.Path(__file__).parent))
from agent import FredFixAgent

app = FastAPI()
agent = FredFixAgent()

class CommandRequest(BaseModel):
    """A request model for commands."""
    command: str

@app.post("/run")
async def run_command(req: CommandRequest):
    """Runs a command on the agent."""
    result = agent.run_agent(req.command)
    return result

@app.get("/")
async def root():
    """The root endpoint of the API."""
    return {"status": "ok", "message": "FredFix AI Agent API is running."}
