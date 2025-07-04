"""
ChatterFix Backend Safety Hub Logic
This file contains the business logic for managing safety incidents and meetings.
"""

from datetime import datetime
from typing import List
from . import database, models, work_orders

# --- Safety Incident Management ---

def report_incident(incident_type: str, location: str, description: str, severity: str, reported_by: str, involved_parties: List[str] = [], corrective_action_taken: str = "", create_work_order: bool = False) -> str:
    """
    Reports a new safety incident and saves it to the database.
    If create_work_order is True, it generates a maintenance work order.
    """
    if incident_type not in models.SafetyIncident.__annotations__['incident_type'].__args__:
        raise ValueError(f"Invalid incident type: {incident_type}")
    if severity not in models.SafetyIncident.__annotations__['severity'].__args__:
        raise ValueError(f"Invalid severity level: {severity}")

    new_incident = models.SafetyIncident(
        id=None, # Firestore will generate
        incident_type=incident_type,
        location=location,
        description=description,
        severity=severity,
        reported_by=reported_by,
        involved_parties=involved_parties,
        corrective_action_taken=corrective_action_taken,
        status='open'
    )

    incident_data = new_incident.__dict__
    doc_id = database.add_document("safety_incidents", incident_data)
    database.update_document("safety_incidents", doc_id, {"id": doc_id})

    # If the incident requires maintenance, automatically generate a work order
    if create_work_order:
        try:
            wo_title = f"Safety Incident Response: {incident_type} at {location}"
            wo_description = f"A safety incident was reported and requires maintenance attention.\n\nIncident Details: {description}"
            
            work_orders.create_work_order(
                title=wo_title,
                description=wo_description,
                priority='critical', # Safety-related work is always critical
                status='open'
            )
            print(f"✅ Automatically created work order for safety incident {doc_id}")
        except Exception as e:
            print(f"🚨 Failed to create work order for safety incident {doc_id}: {e}")

    print(f"✅ Reported safety incident: {doc_id}")
    return doc_id

def get_all_incidents() -> list[models.SafetyIncident]:
    """Retrieves all safety incidents, newest first."""
    all_docs = database.get_collection("safety_incidents")
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
    return [models.SafetyIncident(**doc) for doc in all_docs_sorted]

def update_incident_status(incident_id: str, status: str, corrective_action: str = "") -> None:
    """Updates an incident's status and corrective action notes."""
    if status not in models.SafetyIncident.__annotations__['status'].__args__:
        raise ValueError(f"Invalid status: {status}")
    updates = {"status": status}
    if corrective_action:
        updates['corrective_action_taken'] = corrective_action
    database.update_document("safety_incidents", incident_id, updates)
    print(f"✅ Updated incident {incident_id} to {status}")

# --- Safety Meeting Management ---

def log_safety_meeting(topic: str, attendees: List[str], conducted_by: str, notes: str = "") -> str:
    """
    Logs a new safety meeting and saves it to the database.
    """
    new_meeting = models.SafetyMeeting(
        id=None, # Firestore will generate
        topic=topic,
        attendees=attendees,
        conducted_by=conducted_by,
        notes=notes
    )
    meeting_data = new_meeting.__dict__
    doc_id = database.add_document("safety_meetings", meeting_data)
    database.update_document("safety_meetings", doc_id, {"id": doc_id})
    print(f"✅ Logged safety meeting: {doc_id}")
    return doc_id

def get_all_safety_meetings() -> list[models.SafetyMeeting]:
    """Retrieves all safety meetings, newest first."""
    all_docs = database.get_collection("safety_meetings")
    all_docs_sorted = sorted(all_docs, key=lambda x: x.get('timestamp', datetime.min), reverse=True)
    return [models.SafetyMeeting(**doc) for doc in all_docs_sorted]
