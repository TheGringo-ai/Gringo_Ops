import os
import subprocess
from dotenv import load_dotenv

load_dotenv()  # fallback if Keychain fails

def get_key(service_name: str) -> str:
    """Returns secret from macOS Keychain, or .env fallback."""
    try:
        result = subprocess.check_output(
            ['security', 'find-generic-password', '-s', service_name, '-w'],
            stderr=subprocess.DEVNULL
        )
        return result.decode().strip()
    except subprocess.CalledProcessError:
        return os.getenv(service_name.upper(), "")
