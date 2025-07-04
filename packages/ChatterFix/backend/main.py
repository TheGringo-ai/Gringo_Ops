from fastapi import FastAPI, HTTPException
from google.cloud import firestore
import os
import sys

# Add the utils directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../utils')))
from logging_config import setup_logging

# Set up structured logging
logger = setup_logging()

app = FastAPI()

db = firestore.Client()

@app.get("/")
def index():

    """Placeholder docstring for index."""    logger.info("Root endpoint was called.")
    return {"status": "ok", "message": "Welcome to the ChatterFix API!"}

@app.get("/firestore-test")
def firestore_test():
    """An endpoint to explicitly test the Firestore connection."""
    logger.info("Firestore test endpoint was called.")
    try:
        doc_ref = db.collection("debug").document("ping")
        doc_ref.set({"status": "ok", "timestamp": firestore.SERVER_TIMESTAMP})
        doc = doc_ref.get()
        if doc.exists:
            logger.info("Firestore connection test successful.")
            return {"status": "success", "message": "Successfully connected to Firestore and performed a write/read operation. ✅"}
        else:
            logger.error("Firestore write operation failed.")
            raise HTTPException(status_code=500, detail="Write operation seemed to succeed, but could not read the document back.")

    except Exception as e:
        logger.error(f"An unexpected error occurred during Firestore test: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

# The Gunicorn server in the Dockerfile will run this app.
