import json
import firebase_admin
from firebase_admin import credentials
from google.cloud import secretmanager


def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/487771372565/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


def show_key(label, key):
    if key and len(key) > 10:
        print(f"✅ {label}: {key[:6]}...{key[-4:]}")
    else:
        print(f"❌ {label}: Missing or too short")


def init_firebase():
    print("\n🔐 Initializing Firebase Admin...")
    try:
        firebase_json = get_secret("chatterfix-service-account")
        cred = credentials.Certificate(json.loads(firebase_json))
        firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin SDK initialized")
    except Exception as e:
        print(f"❌ Firebase init failed: {e}")


def test_keys():
    print("\n🔑 Verifying Secret Manager Keys...\n")

    try:
        show_key("OPENAI_API_KEY", get_secret("openai-api-key"))
    except Exception as e:
        print(f"❌ OPENAI_API_KEY fetch failed: {e}")

    try:
        show_key("GEMINI_API_KEY", get_secret("gemini-api-key"))
    except Exception as e:
        print(f"❌ GEMINI_API_KEY fetch failed: {e}")

    try:
        show_key("GITHUB_API_KEY", get_secret("GitCentral1-github-oauthtoken-72aaaa"))
    except Exception as e:
        print(f"❌ GITHUB_API_KEY fetch failed: {e}")

    try:
        show_key("GOOGLE_WORKSPACE_KEY", get_secret("Google"))
    except Exception as e:
        print(f"⚠️  GOOGLE_WORKSPACE_KEY might be optional: {e}")

    try:
        show_key("HUGGINGFACE_API_KEY", get_secret("huggingface-api-key"))
    except Exception:
        print("ℹ️  HUGGINGFACE_API_KEY not found (optional).")


if __name__ == "__main__":
    print("\n🚀 God Mode Keychain Diagnostic\n" + "="*35)
    init_firebase()
    test_keys()
    print("\n✅ Key test complete.\n")
