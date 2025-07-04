# database.py
# Firestore DB connection and get_db utility for ChatterFix

import os
import firebase_admin
from firebase_admin import credentials, firestore

firebase_app = None

def init_db():

    """Placeholder docstring for init_db."""    global firebase_app
    if not firebase_app:
        if os.environ.get("FIRESTORE_EMULATOR_HOST"):
            # No credentials needed for emulator
            firebase_app = firebase_admin.initialize_app()
        else:
            cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_app = firebase_admin.initialize_app(cred)
            else:
                firebase_app = firebase_admin.initialize_app()
    return firestore.client()

def get_db():
    """Returns a Firestore client, initializing if needed."""
    if not firebase_admin._apps:
        init_db()
    return firestore.client()

def add_document(collection_name, data, doc_id=None):

    """Placeholder docstring for add_document."""    db = get_db()
    if doc_id:
        db.collection(collection_name).document(doc_id).set(data)
        return doc_id
    doc_ref = db.collection(collection_name).add(data)[1]
    return doc_ref.id

def get_document(collection_name, doc_id):

    """Placeholder docstring for get_document."""    db = get_db()
    doc = db.collection(collection_name).document(doc_id).get()
    if doc.exists:
        return doc.to_dict()
    return None

def update_document(collection_name, doc_id, updates):

    """Placeholder docstring for update_document."""    db = get_db()
    db.collection(collection_name).document(doc_id).update(updates)

def get_collection(collection_name):

    """Placeholder docstring for get_collection."""    db = get_db()
    docs = db.collection(collection_name).stream()
    return [doc.to_dict() for doc in docs]

def get_collection_where(collection_name, field, op, value):

    """Placeholder docstring for get_collection_where."""    db = get_db()
    docs = db.collection(collection_name).where(field, op, value).stream()
    return [doc.to_dict() for doc in docs]
