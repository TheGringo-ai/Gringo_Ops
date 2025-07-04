from .models import WorkOrder
from datetime import datetime

# In-memory fake DB
WORK_ORDERS = [
    WorkOrder(1, "Fix Conveyor", "Motor jammed", "Open", "High", "Bob", datetime.now(), None),
    WorkOrder(2, "Replace Filter", "Quarterly PM", "In Progress", "Medium", "Alice", datetime.now(), None),
]

def load_work_orders():
    return WORK_ORDERS

def save_work_order(order: WorkOrder):
    WORK_ORDERS.append(order)
