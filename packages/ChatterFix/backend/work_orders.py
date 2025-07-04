"""
ChatterFix Backend Work Order Management Logic
This file contains the core business logic for creating and managing work orders.
"""

from datetime import datetime
from google.cloud import firestore # Import firestore
from . import database
from . import models
from .audit import log_action

# --- Work Order Management ---

@log_action
def create_work_order(title: str, description: str, priority: str, equipment_id: str = "", status: str = "open", invoked_by_user: str = "system") -> str:
    """
    Creates a new work order and saves it to the database.
    Returns the ID of the newly created work order.
    """
    # Validate the provided status
    if status not in models.WorkOrder.STATUS_OPTIONS:
        raise ValueError(f"Invalid status: '{status}'")

    new_work_order = models.WorkOrder(
        id=None,  # Firestore will generate this
        title=title,
        description=description,
        status=status,  # Use the provided status
        priority=priority,
        equipment_id=equipment_id,
    )

    # Convert dataclass to dict for Firestore
    work_order_data = new_work_order.__dict__
    # Firestore expects datetime objects, not factory functions
    work_order_data['created_at'] = datetime.utcnow()
    work_order_data['created_by'] = invoked_by_user # Add the user who created the work order


    # Add to database
    doc_id = database.add_document("work_orders", work_order_data)

    # Now update the object with the ID from Firestore
    database.update_document("work_orders", doc_id, {"id": doc_id})

    print(f"✅ Created work order: {doc_id}")
    return doc_id

def get_work_order(work_order_id: str) -> models.WorkOrder | None:
    """Retrieves a single work order by its ID."""
    data = database.get_document("work_orders", work_order_id)
    if data:
        return models.WorkOrder(**data)
    return None

def get_all_work_orders() -> list[models.WorkOrder]:
    """Retrieves all work orders from the database."""
    all_docs = database.get_collection("work_orders")
    # Sort by creation date, newest first
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('created_at', datetime.min), reverse=True)
    return [models.WorkOrder(**doc) for doc in all_docs_sorted]


def get_work_orders_by_status(status: str) -> list[models.WorkOrder]:
    """Retrieves all work orders from the database with a specific status."""
    all_docs = database.get_collection_where("work_orders", "status", "==", status)
    # Sort by creation date, newest first
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('created_at', datetime.min), reverse=True)
    return [models.WorkOrder(**doc) for doc in all_docs_sorted]


def update_work_order_status(work_order_id: str, new_status: str, user: str, invoked_by_user: str = "system") -> None:
    """Updates the status of a work order and logs the change."""
    if new_status not in models.WorkOrder.STATUS_OPTIONS:
        raise ValueError(f"Invalid status: {new_status}")

    update_data = {"status": new_status}
    add_work_order_history(work_order_id, user, f"Status changed to '{new_status}'.")
    database.update_document("work_orders", work_order_id, update_data)
    print(f"✅ Updated status for work order {work_order_id} to '{new_status}'.")

def assign_work_order(work_order_id: str, assignee_id: str, user: str, invoked_by_user: str = "system") -> None:
    """Assigns a work order to a user and logs the change."""
    update_data = {"assigned_to_id": assignee_id}
    # We need to get the username from the ID for a more descriptive log.
    # This is a simplified example. In a real app, you'd fetch the user's details.
    assignee_name = f"user ({assignee_id})" if assignee_id else "Unassigned"
    add_work_order_history(work_order_id, user, f"Assigned to {assignee_name}.")
    database.update_document("work_orders", work_order_id, update_data)
    print(f"✅ Assigned work order {work_order_id} to '{assignee_id}'.")

def add_work_order_history(work_order_id: str, user: str, action: str, invoked_by_user: str = "system") -> None:
    """Adds a new entry to the work order's history log."""
    history_entry = {
        "timestamp": datetime.utcnow(),
        "user": user,
        "action": action,
    }
    # Firestore's FieldValue.array_union ensures the entry is added to the array.
    update_data = {"history": firestore.ArrayUnion([history_entry])}
    database.update_document("work_orders", work_order_id, update_data)
    print(f"✅ Logged history for work order {work_order_id}: '{action}'")
