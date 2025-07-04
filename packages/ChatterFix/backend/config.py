import os
import firebase_admin
from firebase_admin import credentials
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Key Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
GITHUB_API_KEY = os.getenv("GITHUB_API_KEY")

# --- Firebase Configuration ---
SERVICE_ACCOUNT_KEY_PATH = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")

if SERVICE_ACCOUNT_KEY_PATH:
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase Admin SDK: {e}")
else:
    print("⚠️ FIREBASE_SERVICE_ACCOUNT_KEY_PATH not set. Firebase integration will be disabled.")

# --- Model Configuration ---
AUTO_RESOLVE_MODEL = os.getenv("DEFAULT_AI_MODEL", "").lower()

# Helper: prompt user to resolve model disagreement
def resolve_conflict(openai_output, gemini_output):
    """Placeholder docstring for resolve_conflict."""    if AUTO_RESOLVE_MODEL in ['o', 'g']:
        print(f"\n⚙️ AUTO-RESOLVE ENABLED: Using {'OpenAI' if AUTO_RESOLVE_MODEL == 'o' else 'Gemini'} by default.")
        return AUTO_RESOLVE_MODEL

    print("\n🤖 Models disagreed. Here's what each said:")
    print("\n--- OpenAI Suggestion ---\n")
    print(openai_output)
    print("\n--- Gemini Suggestion ---\n")
    print(gemini_output)
    print("\nYou are the boss. Choose:")
    print("  (o) Use OpenAI suggestion")
    print("  (g) Use Gemini suggestion")
    print("  (s) Skip applying either")

    while True:
        choice = input("Your decision (o/g/s): ").strip().lower()
        if choice in ['o', 'g', 's']:
            return choice
        else:
            print("Invalid choice. Please enter 'o', 'g', or 's'.")