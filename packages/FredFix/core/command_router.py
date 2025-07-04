import firebase_admin
from firebase_admin import credentials, firestore

# --- Firebase Initialization ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("gcp-service-account-key.json")
    except FileNotFoundError:
        # This is a fallback for local development
        # In production, the service account key should be set as an environment variable
        cred = None
    
    firebase_admin.initialize_app(cred)

db = firestore.client()

def check_quota(user_id):
    """
    Checks if a user has exceeded their command quota.
    Returns True if the user has quota remaining, False otherwise.
    """
    if not user_id or user_id == "default_user":
        # For now, we'll allow unlimited commands for the default user
        return True

    usage_ref = db.collection('usage').document(user_id)
    usage_doc = usage_ref.get()

    if not usage_doc.exists:
        # If the user has no usage document, create one with the default quota
        usage_ref.set({
            'command_count': 0,
            'limit': 100,
            'period_start': firestore.SERVER_TIMESTAMP
        })
        return True

    usage_data = usage_doc.to_dict()
    
    # In a real app, you'd also check the period_start to reset the quota monthly
    
    if usage_data['command_count'] < usage_data['limit']:
        # Increment the command count
        usage_ref.update({'command_count': firestore.Increment(1)})
        return True
    else:
        return False

def execute_command(command: str, memory: dict, user_id="default_user"):
    """Executes a command and returns the result."""
    if not check_quota(user_id):
        return "You have exceeded your command quota for this month. Please upgrade to a paid plan to continue."
        
    if command == "hello":
        return "👋 Hello from FredFix!"
    elif command == "status":
        return f"📦 Current memory keys: {list(memory.keys())}"
    elif command.startswith("create work order"):
        task_description = command.replace("create work order", "").strip()
        if not task_description:
            return "Please provide a description for the work order."
        
        # In a real app, this would create a record in a database.
        # For now, we'll just format it nicely.
        return f"""
        **New Work Order Created**
        ---
        **Task:** {task_description}
        **Status:** Open
        **Priority:** Medium (auto-assigned)
        **Assigned To:** Unassigned
        """
    else:
        return f"❓ Unknown command: '{command}'"
