"""
ChatterFix Backend Quality Control Logic
This file contains the business logic for managing quality checks.
"""

from datetime import datetime
from . import database, models, work_orders

def create_quality_check(asset_id: str, check_type: str, status: str, notes: str = "", checked_by: str = "") -> str:
    """
    Creates a new quality check and saves it to the database.
    If the check fails, it can optionally trigger a new work order.
    """
    if status not in models.QualityCheck.__annotations__['status'].__args__:
        raise ValueError(f"Invalid status: {status}")

    new_check = models.QualityCheck(
        id=None, # Firestore will generate
        asset_id=asset_id,
        check_type=check_type,
        status=status,
        notes=notes,
        checked_by=checked_by
    )

    check_data = new_check.__dict__
    doc_id = database.add_document("quality_checks", check_data)
    database.update_document("quality_checks", doc_id, {"id": doc_id})

    # If a check fails, automatically generate a work order
    if status == 'fail':
        try:
            asset = database.get_document("assets", asset_id)
            asset_name = asset.get('name', 'Unknown Asset') if asset else 'Unknown Asset'
            wo_title = f"Quality Check Failed for {asset_name}"
            wo_description = f"A quality check of type '{check_type}' failed.\n\nInspector Notes: {notes}"
            
            work_orders.create_work_order(
                title=wo_title,
                description=wo_description,
                priority='high', # Failed checks are usually high priority
                equipment_id=asset_id,
                status='open'
            )
            print(f"✅ Automatically created work order for failed check {doc_id}")
        except Exception as e:
            print(f"🚨 Failed to create work order for failed check {doc_id}: {e}")


    print(f"✅ Created quality check: {doc_id}")
    return doc_id

def get_quality_check(check_id: str) -> models.QualityCheck | None:
    """Retrieves a single quality check by its ID."""
    data = database.get_document("quality_checks", check_id)
    if data:
        return models.QualityCheck(**data)
    return None

def get_all_quality_checks() -> list[models.QualityCheck]:
    """Retrieves all quality checks, newest first."""
    all_docs = database.get_collection("quality_checks")
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
    return [models.QualityCheck(**doc) for doc in all_docs_sorted]

def get_quality_checks_for_asset(asset_id: str) -> list[models.QualityCheck]:
    """Retrieves all quality checks for a specific asset."""
    all_docs = database.get_collection_where("quality_checks", "asset_id", "==", asset_id)
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
    return [models.QualityCheck(**doc) for doc in all_docs_sorted]

def update_quality_check(check_id: str, updates: dict) -> None:
    """Updates a quality check's details."""
    database.update_document("quality_checks", check_id, updates)
    print(f"✅ Updated quality check: {check_id}")
