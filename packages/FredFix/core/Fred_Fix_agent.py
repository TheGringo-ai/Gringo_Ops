import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pathlib
import os
import logging

# Ensure the parent directory is in sys.path for import
sys.path.append(str(pathlib.Path(__file__).parent))
from agent import FredFixAgent

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fredfix_agent")

# API key for authentication (set FRED_FIX_API_KEY in env)
API_KEY = os.getenv("FRED_FIX_API_KEY")

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = FredFixAgent()

class CommandRequest(BaseModel):
    """Placeholder docstring for CommandRequest."""    command: str

# Dependency for API key authentication
def verify_api_key(x_api_key: str = None):
    """Placeholder docstring for verify_api_key."""    if not API_KEY:
        logger.warning("FRED_FIX_API_KEY not set in environment!")
        return
    if x_api_key != API_KEY:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid or missing API Key.")

from fastapi import Header, Depends, HTTPException

@app.post("/run")
async def run_command(req: CommandRequest, x_api_key: str = Header(None)):
    """Placeholder docstring for run_command."""    verify_api_key(x_api_key)
    try:
        result = agent.run_agent(req.command)
        return {"result": result}
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- ChatterFix /chat endpoint template ---
class ChatRequest(BaseModel):
    """Placeholder docstring for ChatRequest."""    message: str
    user_id: str = None

@app.post("/chat")
async def chat_endpoint(req: ChatRequest, x_api_key: str = Header(None)):
    """Placeholder docstring for chat_endpoint."""    verify_api_key(x_api_key)
    try:
        # Placeholder: route to FredFixAgent or ChatterFix logic
        response = agent.run_agent(req.message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Placeholder docstring for root."""    return {"status": "ok", "message": "FredFix AI Agent API is running."}
