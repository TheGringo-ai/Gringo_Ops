"""
ERP (Enterprise Resource Planning) Tools
This module provides hooks into a simulated ERP system for managing vendors,
financials, and procurement. In a real-world scenario, these functions would
integrate with systems like SAP, Oracle, or NetSuite.
"""

from .audit import log_action


@log_action
def get_vendor_data(part_number: str, invoked_by_user: str = "system") -> dict:
    """
    Looks up vendor and pricing information for a given part number.
    Returns a dictionary with vendor details or an empty dict if not found.
    """
    print(f"ERP: Searching for vendors for part {part_number}...")
    # In a real system, this would query the ERP database.
    # For now, returning mock data.
    if "BR-54321" in part_number:
        return {
            "primary_vendor": "Global Bearings Inc.",
            "price": 15.99,
            "lead_time_days": 7
        }
    return {}


@log_action
def create_financial_report(report_type: str, period: str, invoked_by_user: str = "system") -> dict:
    """
    Generates a financial report (e.g., cost analysis, budget variance).
    Returns a dictionary representing the report.
    """
    print(f"ERP: Generating {report_type} report for {period}...")
    # Mock implementation
    return {
        "report_id": f"FIN-REP-{hash(report_type + period)}",
        "status": "generated",
        "message": f"{report_type} report for {period} is ready."
    }


@log_action
def check_budget_limits(department: str, amount: float, invoked_by_user: str = "system") -> bool:
    """
    Checks if a proposed expenditure is within the department's budget.
    Returns True if within budget, False otherwise.
    """
    print(f"ERP: Checking budget for {department} for amount {amount}...")
    # Mock implementation: Maintenance always has budget
    if department == "maintenance":
        return True
    return False


@log_action
def generate_purchase_order(part_number: str, quantity: int, vendor: str, invoked_by_user: str = "system") -> dict:
    """
    Creates a purchase order (PO) in the ERP system.
    Returns a dictionary with the PO details.
    """
    print(f"ERP: Generating PO for {quantity} of {part_number} from {vendor}...")
    # Mock implementation
    po_number = f"PO-{hash(part_number + str(quantity))}"
    return {
        "po_number": po_number,
        "status": "submitted",
        "message": f"Purchase order {po_number} has been submitted to {vendor}."
    }
