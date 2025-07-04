# models.py
# ChatterFix backend models

from typing import Optional, List, ClassVar
from pydantic import BaseModel
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='user')

    def __repr__(self):
    """Incorrectly indented docstring."""
        return f"<User(username='{self.username}')>"

class Asset(Base):
    __tablename__ = 'assets'
    id: Optional[str] = None
    name: str
    asset_type: str
    location: str
    purchase_date: str
    purchase_price: float
    serial_number: str
    status: str
    qr_code_url: Optional[str] = None
    STATUS_OPTIONS: ClassVar[list[str]] = ["active", "maintenance", "retired", "decommissioned"]

class Part(BaseModel):
    """Placeholder docstring for Part."""    id: Optional[str] = None
    name: str
    part_number: str
    stock_quantity: int
    location: str
    category: str
    low_stock_threshold: int
    supplier: Optional[str] = None

class WorkOrder(BaseModel):
    """Placeholder docstring for WorkOrder."""    id: Optional[str] = None
    title: str
    description: str
    status: str
    priority: str
    equipment_id: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    assigned_to_id: Optional[str] = None
    history: list[dict] = []
    STATUS_OPTIONS: ClassVar[list[str]] = ["open", "in_progress", "completed", "cancelled"]

class Supplier(BaseModel):
    """Placeholder docstring for Supplier."""    id: Optional[str] = None
    name: str
    contact_email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class BillOfMaterials(BaseModel):
    """Placeholder docstring for BillOfMaterials."""    id: Optional[str] = None
    name: str
    items: list[str] = []
    description: Optional[str] = None
    components: list[dict] = []

class PurchaseOrder(BaseModel):
    """Placeholder docstring for PurchaseOrder."""    id: Optional[str] = None
    order_number: Optional[str] = None
    supplier_id: str
    items: list[dict] = []  # Accept list of dicts for item details
    total_cost: Optional[float] = None
    created_by: Optional[str] = None
    status: str
    notes: Optional[str] = None
    order_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    received_at: Optional[datetime] = None

class ProductionOrder(BaseModel):
    """Placeholder docstring for ProductionOrder."""    id: Optional[str] = None
    order_number: Optional[str] = None
    product_name: Optional[str] = None
    bom_id: Optional[str] = None
    quantity: int
    status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    STATUS_OPTIONS: ClassVar[list[str]] = ["scheduled", "in_progress", "completed", "cancelled"]
