"""
Centralized Audit Logging for ChatterFix

This module provides a decorator to log critical actions (tool executions)
to a dedicated Firestore collection. This creates an immutable audit trail.
"""
import functools
from datetime import datetime, timezone
from .database import get_db

def log_action(func):
    """
    Decorator to log the execution of a tool to the Firestore 'audit_log' collection.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # The username should be passed as a keyword argument to the tool
        username = kwargs.get("invoked_by_user", "unknown")
        action_time = datetime.now(timezone.utc)
        
        # Execute the original function to get the result
        try:
            result = func(*args, **kwargs)
            status = "success"
            result_summary = str(result)[:500] # Truncate long results
        except Exception as e:
            status = "error"
            result_summary = str(e)
            # Re-raise the exception so the original caller can handle it
            raise

        # Prepare the log entry
        log_entry = {
            "user": username,
            "action": func.__name__,
            "parameters": args,
            "keyword_parameters": kwargs,
            "timestamp": action_time,
            "status": status,
            "result": result_summary
        }

        # Write the log to Firestore
        try:
            db = get_db()
            db.collection('audit_log').add(log_entry)
            print(f"✅ Audit log created for action: {func.__name__}")
        except Exception as e:
            # If logging fails, print an error but don't crash the application
            print(f"❌ Failed to write to audit log: {e}")
            
        return result
    return wrapper
