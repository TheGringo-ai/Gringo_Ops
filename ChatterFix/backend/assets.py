"""
ChatterFix Backend Asset Management Logic
This file contains the core business logic for creating and managing assets.
"""

from datetime import datetime
from . import database
from . import models
from . import qr_utils
from .audit import log_action

# --- Asset Management ---

@log_action
def create_asset(name: str, asset_type: str, location: str, purchase_date: str, purchase_price: float, serial_number: str, invoked_by_user: str = "system") -> str:
    """
    Creates a new asset and saves it to the database.
    Returns the ID of the newly created asset.
    """
    new_asset = models.Asset(
        id=None,  # Firestore will generate this
        name=name,
        asset_type=asset_type,
        location=location,
        purchase_date=purchase_date,
        purchase_price=purchase_price,
        serial_number=serial_number,
        status='active',
        qr_code_url="", # Initialize with empty string
    )
    
    # Convert dataclass to dict for Firestore
    asset_data = new_asset.__dict__
    
    # Add to database
    doc_id = database.add_document("assets", asset_data)

    # Generate QR code with the asset's new ID
    qr_code_data = f"asset_id:{doc_id}"
    qr_code_url = qr_utils.generate_qr_code_base64(qr_code_data)
    
    # Now update the object with the ID and QR code from Firestore
    database.update_document("assets", doc_id, {"id": doc_id, "qr_code_url": qr_code_url})
    
    print(f"✅ Created asset: {doc_id}")
    return doc_id

def get_asset(asset_id: str) -> models.Asset | None:
    """Retrieves a single asset by its ID."""
    data = database.get_document("assets", asset_id)
    if data:
        return models.Asset(**data)
    return None

def get_all_assets() -> list[models.Asset]:
    """Retrieves all assets from the database."""
    all_docs = database.get_collection("assets")
    return [models.Asset(**doc) for doc in all_docs]

@log_action
def update_asset_status(asset_id: str, new_status: str, user: str, invoked_by_user: str = "system") -> None:
    """Updates the status of an asset and logs the change."""
    if new_status not in models.Asset.STATUS_OPTIONS:
        raise ValueError(f"Invalid status: {new_status}")

    update_data = {"status": new_status}
    database.update_document("assets", asset_id, update_data)
    print(f"✅ Updated status for asset {asset_id} to '{new_status}'.")
