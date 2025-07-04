"""
ChatterFix Backend Parts Management Logic
This file contains the core business logic for creating and managing parts.
"""

from . import database
from . import models
from . import qr_utils

# --- Part Management ---

def create_part(name: str, part_number: str, stock_quantity: int, location: str, supplier: str = "", category: str = "Uncategorized", low_stock_threshold: int = 5) -> str:
    """
    Creates a new part and saves it to the database.
    Returns the ID of the newly created part.
    """
    new_part = models.Part(
        id=None,  # Firestore will generate this
        name=name,
        part_number=part_number,
        stock_quantity=stock_quantity,
        location=location,
        supplier=supplier,
        category=category,
        low_stock_threshold=low_stock_threshold,
        qr_code_url="", # Initialize with empty string
    )
    
    # Convert dataclass to dict for Firestore
    part_data = new_part.__dict__
    
    # Add to database
    doc_id = database.add_document("parts", part_data)
    
    # Generate QR code with the part's new ID
    qr_code_data = f"part_id:{doc_id}"
    qr_code_url = qr_utils.generate_qr_code_base64(qr_code_data)

    # Now update the object with the ID and QR code from Firestore
    database.update_document("parts", doc_id, {"id": doc_id, "qr_code_url": qr_code_url})
    
    print(f"✅ Created part: {doc_id}")
    return doc_id

def get_part(part_id: str) -> models.Part | None:
    """Retrieves a single part by its ID."""
    data = database.get_document("parts", part_id)
    if data:
        return models.Part(**data)
    return None

def get_all_parts() -> list[models.Part]:
    """Retrieves all parts from the database."""
    all_docs = database.get_collection("parts")
    return [models.Part(**doc) for doc in all_docs]

def update_part_stock(part_id: str, quantity_change: int, user: str) -> None:
    """Updates the stock quantity of a part."""
    part = get_part(part_id)
    if part:
        new_quantity = part.stock_quantity + quantity_change
        update_data = {"stock_quantity": new_quantity}
        database.update_document("parts", part_id, update_data)
        print(f"✅ Updated stock for part {part_id} to {new_quantity}.")
    else:
        print(f"❌ Part with ID {part_id} not found.")
