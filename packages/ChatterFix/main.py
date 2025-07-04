import sys
from backend import database

print("--- Running Pre-flight Initialization Check ---")
try:
    # This line will trigger the initialization in database.py by calling the function
    database.get_db()
    print("✅ Firebase Initialized Successfully.")
    sys.exit(0) # Exit with success code
except Exception as e:
    print(f"CRITICAL: Failed to initialize Firebase: {e}", file=sys.stderr)
    sys.exit(1) # Exit with failure code
