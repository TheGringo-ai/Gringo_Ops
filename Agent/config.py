
import os
import platform
import subprocess
from typing import Optional

try:
    from google.cloud import secretmanager
    from google.auth.exceptions import DefaultCredentialsError
    GCP_ENABLED = True
except ImportError:
    GCP_ENABLED = False

def load_from_gcp_secret_manager(secret_id: str) -> Optional[str]:
    if not GCP_ENABLED:
        return None
    try:
        client = secretmanager.SecretManagerServiceClient()
        project_id = os.getenv("GCP_PROJECT_ID", "your-default-project-id")
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"⚠️ GCP Secret load failed for {secret_id}: {e}")
        return None

def load_from_keychain(service: str) -> Optional[str]:
    if platform.system() != "Darwin":
        return None
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', service, '-w'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        print(f"⚠️ Keychain error for {service}: {e}")
    return None

def load_secret(service: str) -> str:
    for source in (load_from_gcp_secret_manager, load_from_keychain, os.getenv):
        value = source(service)
        if value:
            print(f"✅ Loaded {service} from {source.__name__}")
            return value.strip()
    raise RuntimeError(f"❌ Failed to load secret: {service}")

SECRETS = {}
REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "GEMINI_API_KEY",
    "HUGGINGFACE_API_KEY",
    "GITHUB_API_KEY"
]

for key in REQUIRED_KEYS:
    try:
        SECRETS[key] = load_secret(key)
    except Exception as e:
        print(e)
