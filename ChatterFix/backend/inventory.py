"""
ChatterFix Backend Inventory and Warehouse Management Logic
This file contains the business logic for managing parts, stock levels, and suppliers.
"""
from . import database, models
from .audit import log_action
from google.cloud import firestore

# --- Part & Inventory Management ---

@log_action
def add_part(name: str, part_number: str, stock_quantity: int, location: str, category: str, low_stock_threshold: int, supplier: str = "", invoked_by_user: str = "system") -> str:
    """
    Adds a new part to the inventory.
    """
    new_part = models.Part(
        id=None, # Firestore will generate
        name=name,
        part_number=part_number,
        stock_quantity=stock_quantity,
        location=location,
        category=category,
        low_stock_threshold=low_stock_threshold,
        supplier=supplier
    )
    part_data = new_part.__dict__
    # Use part_number as the document ID for uniqueness if it's reliable
    doc_id = database.add_document("parts", part_data, doc_id=part_number)
    database.update_document("parts", doc_id, {"id": doc_id})
    print(f"✅ Added part: {doc_id}")
    return doc_id

def get_all_parts() -> list[models.Part]:
    """Retrieves all parts from the database."""
    all_docs = database.get_collection("parts")
    return [models.Part(**doc) for doc in all_docs]

@log_action
def update_part(part_id: str, updates: dict, invoked_by_user: str = "system") -> None:
    """Updates a part's details in the database."""
    database.update_document("parts", part_id, updates)
    print(f"✅ Updated part: {part_id}")

@log_action
def adjust_stock(part_id: str, quantity_change: int, user: str, invoked_by_user: str = "system") -> None:
    """
    Adjusts the stock quantity of a part by a given amount (can be positive or negative).
    Logs the transaction for auditing purposes.
    """
    if not isinstance(quantity_change, int):
        raise ValueError("Quantity change must be an integer.")

    update_data = {"stock_quantity": firestore.Increment(quantity_change)}
    database.update_document("parts", part_id, update_data)
    
    # TODO: Integrate with a more robust transaction/ledger system in the future
    # For now, we can log this to the part's history or a general ledger
    print(f"✅ Adjusted stock for part {part_id} by {quantity_change}. User: {user}.")


def get_low_stock_parts() -> list[models.Part]:
    """
    Scans the inventory and returns a list of all parts where the
    stock quantity is at or below the low_stock_threshold.
    """
    all_parts = get_all_parts()
    low_stock_items = [
        part for part in all_parts 
        if part.stock_quantity <= part.low_stock_threshold
    ]
    return low_stock_items

def get_part_by_id(part_id: str) -> models.Part | None:
    """Retrieves a single part by its ID."""
    data = database.get_document("parts", part_id)
    if data:
        return models.Part(**data)
    return None

def get_part(part_id: str) -> models.Part | None:
    """Alias for get_part_by_id for compatibility with production logic."""
    return get_part_by_id(part_id)
