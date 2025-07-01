"""
ChatterFix Backend Document Management Logic
This file contains the core business logic for uploading, downloading, 
and managing documents using Firebase Storage.
"""

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from google.cloud import storage
from . import database
from . import models
from ..config import BUCKET_NAME

# Initialize Firebase Storage
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

def upload_document(file, related_to_id: str, uploaded_by: str) -> str:
    """
    Uploads a file to Firebase Storage and saves its metadata to Firestore.
    Returns the ID of the newly created document record.
    """
    if not file:
        raise ValueError("No file provided.")

    filename = secure_filename(file.name)
    blob = bucket.blob(f"documents/{filename}")

    # Upload the file
    blob.upload_from_file(file)

    # Create a document record in Firestore
    new_document = models.Document(
        id=None, # Firestore will generate
        file_name=filename,
        file_type=file.type,
        file_size=file.size,
        storage_path=blob.public_url,
        related_to_id=related_to_id,
        uploaded_by=uploaded_by,
    )

    doc_data = new_document.__dict__
    doc_id = database.add_document("documents", doc_data)
    database.update_document("documents", doc_id, {"id": doc_id})

    print(f"✅ Uploaded {filename} and created document record: {doc_id}")
    return doc_id

def get_documents_for(related_id: str) -> list[models.Document]:
    """Retrieves all documents related to a specific ID (e.g., work order)."""
    query = [("related_to_id", "==", related_id)]
    docs = database.get_collection("documents", query)
    return [models.Document(**doc) for doc in docs]

def download_document_link(document_id: str) -> str:
    """Generates a temporary signed URL to download a document."""
    doc = database.get_document("documents", document_id)
    if not doc:
        return None
    
    blob = bucket.blob(f"documents/{doc['file_name']}")
    # Generate a signed URL that expires in 1 hour
    url = blob.generate_signed_url(expiration=datetime.timedelta(hours=1))
    return url
