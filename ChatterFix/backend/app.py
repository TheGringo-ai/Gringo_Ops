
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
sys.path.append('../../lib')
from keychain import get_key

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "ChatterFix API is running."}

@app.get("/key/{service}")
def get_service_key(service: str):
    key = get_key(service)
    return {"service": service, "key": key}
