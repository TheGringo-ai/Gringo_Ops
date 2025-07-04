"""
ChatterFix Backend Accounting Logic
This file contains the core business logic for managing financial transactions.
"""

from datetime import datetime
from . import database
from . import models

# --- Transaction Management ---

def create_transaction(transaction_type: str, amount: float, description: str, related_to_id: str) -> str:
    """
    Creates a new transaction and saves it to the database.
    Returns the ID of the newly created transaction.
    """
    new_transaction = models.Transaction(
        id=None,  # Firestore will generate this
        transaction_type=transaction_type,
        amount=amount,
        description=description,
        related_to_id=related_to_id,
    )

    # Convert dataclass to dict for Firestore
    transaction_data = new_transaction.__dict__
    transaction_data['transaction_date'] = datetime.utcnow()

    # Add to database
    doc_id = database.add_document("transactions", transaction_data)

    # Now update the object with the ID from Firestore
    database.update_document("transactions", doc_id, {"id": doc_id})

    print(f"✅ Created transaction: {doc_id}")
    return doc_id

def get_transaction(transaction_id: str) -> models.Transaction | None:
    """Retrieves a single transaction by its ID."""
    data = database.get_document("transactions", transaction_id)
    if data:
        return models.Transaction(**data)
    return None

def get_all_transactions() -> list[models.Transaction]:
    """Retrieves all transactions from the database."""
    all_docs = database.get_collection("transactions")
    # Sort by transaction date, newest first
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('transaction_date', datetime.min), reverse=True)
    return [models.Transaction(**doc) for doc in all_docs_sorted]
