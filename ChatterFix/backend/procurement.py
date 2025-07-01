"""
ChatterFix Backend Logic for Supply Chain and Procurement
"""
from datetime import datetime, timedelta
from . import database
from . import models
from . import inventory as inventory_service

# --- Supplier Management ---

def create_supplier(name: str, contact_person: str = "", email: str = "", phone: str = "", address: str = "") -> str:
    """Creates a new supplier."""
    new_supplier = models.Supplier(
        id=None, # Firestore will generate
        name=name,
        contact_person=contact_person,
        email=email,
        phone=phone,
        address=address
    )
    supplier_data = new_supplier.__dict__
    doc_id = database.add_document("suppliers", supplier_data)
    database.update_document("suppliers", doc_id, {"id": doc_id})
    print(f"✅ Created Supplier: {doc_id}")
    return doc_id

def get_all_suppliers() -> list[models.Supplier]:
    """Retrieves all suppliers."""
    all_docs = database.get_collection("suppliers")
    return [models.Supplier(**doc) for doc in all_docs]

def get_supplier(supplier_id: str) -> models.Supplier | None:
    """Retrieves a single supplier by its ID."""
    data = database.get_document("suppliers", supplier_id)
    return models.Supplier(**data) if data else None

def update_supplier(supplier_id: str, updates: dict) -> None:
    """Updates a supplier's details."""
    database.update_document("suppliers", supplier_id, updates)
    print(f"✅ Updated Supplier: {supplier_id}")

# --- Purchase Order Management ---

def create_purchase_order(supplier_id: str, items: list[dict], created_by: str, notes: str = "", status: str = 'pending_approval') -> str:
    """
    Creates a new Purchase Order.
    'items' is a list of dicts: [{'part_id': str, 'quantity': int, 'unit_price': float}]
    """
    total_cost = sum(item['quantity'] * item['unit_price'] for item in items)
    new_po = models.PurchaseOrder(
        id=None, # Firestore will generate
        supplier_id=supplier_id,
        items=items,
        total_cost=total_cost,
        created_by=created_by,
        status=status,
        notes=notes,
        order_date=datetime.utcnow(),
        order_number=None
    )
    po_data = new_po.__dict__
    doc_id = database.add_document("purchase_orders", po_data)
    database.update_document("purchase_orders", doc_id, {"id": doc_id, "order_number": doc_id})
    print(f"✅ Created Purchase Order: {doc_id}")
    return doc_id

def get_all_purchase_orders() -> list[models.PurchaseOrder]:
    """Retrieves all purchase orders."""
    all_docs = database.get_collection("purchase_orders")
    # Sorting should be done client-side if needed, or the get_collection function enhanced
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('order_date'), reverse=True)
    return [models.PurchaseOrder(**doc) for doc in all_docs_sorted]

def get_purchase_order(po_id: str) -> models.PurchaseOrder | None:
    """Retrieves a single purchase order by its ID."""
    data = database.get_document("purchase_orders", po_id)
    return models.PurchaseOrder(**data) if data else None

def update_purchase_order_status(po_id: str, new_status: str) -> None:
    """Updates the status of a purchase order."""
    # Accept any string for now, or define a STATUS_OPTIONS if needed
    allowed_statuses = [
        'pending_approval', 'ordered', 'received', 'cancelled', 'completed'
    ]
    if new_status not in allowed_statuses:
        raise ValueError(f"Invalid status: {new_status}")
    database.update_document("purchase_orders", po_id, {"status": new_status})
    print(f"✅ Updated PO {po_id} status to {new_status}")

def receive_purchase_order_items(po_id: str, received_items: list[dict], user: str) -> str:
    """
    Receives items from a PO and updates stock levels.
    'received_items' is a list of dicts: [{'part_id': str, 'quantity_received': int}]
    """
    po = get_purchase_order(po_id)
    if not po:
        raise ValueError("Purchase Order not found.")

    for item in received_items:
        # Corrected function call from adjust_part_quantity to adjust_stock
        inventory_service.adjust_stock(
            part_id=item['part_id'],
            quantity_change=item['quantity_received'],
            user=user,
            invoked_by_user=f"procurement_receipt for PO {po_id}"
        )

    # Simple logic to mark as received. Could be enhanced to handle partial receipts.
    update_purchase_order_status(po_id, 'received')
    return f"Successfully received items for PO {po_id} and updated inventory."

# --- Automated Procurement ---

def check_inventory_and_generate_po(user_id_for_approval: str) -> list[str]:
    """
    Scans all parts, identifies those below the low stock threshold,
    and generates draft Purchase Orders for them.
    Returns a list of created Purchase Order IDs.
    """
    low_stock_parts = inventory_service.get_low_stock_parts()
    if not low_stock_parts:
        print("ℹ️ No parts are below their low stock threshold.")
        return []

    # Group parts by preferred supplier
    supplier_orders = {}
    for part in low_stock_parts:
        if not part.supplier: # Cannot order if no supplier is set
            continue
        if part.supplier not in supplier_orders:
            supplier_orders[part.supplier] = []
        
        # Simple reorder logic: order 2x the threshold amount
        quantity_to_order = part.low_stock_threshold * 2
        # Assume a placeholder price. This would need a more robust lookup.
        placeholder_price = 1.0 

        supplier_orders[part.supplier].append({
            'part_id': part.id,
            'quantity': quantity_to_order,
            'unit_price': placeholder_price
        })

    created_po_ids = []
    for supplier_id, items in supplier_orders.items():
        po_id = create_purchase_order(
            supplier_id=supplier_id,
            items=items,
            created_by=user_id_for_approval, # Assign to a user for approval
            status='pending_approval',
            notes=f"Auto-generated due to low stock levels."
        )
        created_po_ids.append(po_id)
    
    print(f"✅ Automatically generated {len(created_po_ids)} Purchase Orders.")
    return created_po_ids
