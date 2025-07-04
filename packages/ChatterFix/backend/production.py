"""
ChatterFix Backend Logic for Production Planning
"""
from datetime import datetime
from . import database
from . import models
from . import inventory as inventory_service

def create_bill_of_materials(name: str, description: str, components: list[dict]) -> str:
    """
    Creates a new Bill of Materials (BOM).
    'components' should be a list of dicts, each with 'part_id' and 'quantity'.
    """
    new_bom = models.BillOfMaterials(
        name=name,
        description=description,
        components=components,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    bom_data = new_bom.__dict__
    doc_id = database.add_document("bills_of_materials", bom_data)
    database.update_document("bills_of_materials", doc_id, {"id": doc_id})
    print(f"✅ Created Bill of Materials: {doc_id}")
    return doc_id

def get_bill_of_materials(bom_id: str) -> models.BillOfMaterials | None:
    """Retrieves a single Bill of Materials by its ID."""
    data = database.get_document("bills_of_materials", bom_id)
    return models.BillOfMaterials(**data) if data else None

def get_all_bills_of_materials() -> list[models.BillOfMaterials]:
    """Retrieves all Bills of Materials."""
    all_docs = database.get_collection("bills_of_materials")
    return [models.BillOfMaterials(**doc) for doc in all_docs]

def update_bill_of_materials(bom_id: str, updates: dict) -> None:
    """Updates a Bill of Materials."""
    updates['updated_at'] = datetime.utcnow()
    database.update_document("bills_of_materials", bom_id, updates)
    print(f"✅ Updated Bill of Materials: {bom_id}")

def create_production_order(bom_id: str, quantity: int, notes: str = "") -> str:
    """Creates a new Production Order."""
    bom = get_bill_of_materials(bom_id)
    if not bom:
        raise ValueError("Bill of Materials not found.")

    new_order = models.ProductionOrder(
        bom_id=bom_id,
        quantity=quantity,
        status="Pending",
        notes=notes,
        created_at=datetime.utcnow(),
        order_number=None,
        product_name=bom.name if bom else None
    )
    order_data = new_order.__dict__
    doc_id = database.add_document("production_orders", order_data)
    database.update_document("production_orders", doc_id, {"id": doc_id, "order_number": doc_id})
    print(f"✅ Created Production Order: {doc_id}")
    return doc_id

def get_production_order(order_id: str) -> models.ProductionOrder | None:
    """Retrieves a single Production Order by its ID."""
    data = database.get_document("production_orders", order_id)
    return models.ProductionOrder(**data) if data else None

def get_all_production_orders() -> list[models.ProductionOrder]:
    """Retrieves all Production Orders."""
    all_docs = database.get_collection("production_orders", order_by="created_at", direction="DESCENDING")
    return [models.ProductionOrder(**doc) for doc in all_docs]

def update_production_order_status(order_id: str, new_status: str, user: str) -> str:
    """
    Updates the status of a Production Order and handles inventory adjustments.
    Valid statuses: 'Pending', 'In Progress', 'Completed', 'Cancelled'.
    """
    # Normalize status to lowercase with underscores
    normalized_status = new_status.strip().lower().replace(" ", "_")
    if normalized_status not in models.ProductionOrder.STATUS_OPTIONS:
        raise ValueError(f"Invalid status: {new_status}")

    order = get_production_order(order_id)
    if not order:
        raise ValueError("Production Order not found.")

    # --- Inventory Adjustment Logic ---
    if normalized_status == "in_progress" and order.status == "Pending":
        bom = get_bill_of_materials(order.bom_id)
        if not bom:
            raise ValueError("Bill of Materials for this order not found.")

        # Check for sufficient inventory BEFORE starting production
        for component in bom.components:
            part_id = component['part_id']
            required_quantity = component['quantity'] * order.quantity
            part = inventory_service.get_part(part_id)
            if not part or part.quantity < required_quantity:
                return f"Error: Insufficient stock for part '{part.name if part else part_id}'. Required: {required_quantity}, Available: {part.quantity if part else 0}."

        # Deduct inventory
        for component in bom.components:
            inventory_service.adjust_part_quantity(
                part_id=component['part_id'],
                quantity_change=-(component['quantity'] * order.quantity),
                notes=f"Allocated to Production Order {order_id}"
            )
        print(f"✅ Deducted inventory for Production Order {order_id}")

    database.update_document("production_orders", order_id, {"status": normalized_status})
    print(f"✅ Updated status for Production Order {order_id} to '{normalized_status}'.")
    return f"Success: Production Order {order_id} status updated to '{normalized_status}'."

