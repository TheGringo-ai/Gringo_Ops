import os
import subprocess

def get_key(service_name: str) -> str:
    """Returns secret from macOS Keychain. Raises error if not found."""
    try:
        result = subprocess.check_output(
            ['security', 'find-generic-password', '-s', service_name, '-w'],
            stderr=subprocess.DEVNULL
        )
        print(f"[Keychain] Found secret for: {service_name}")
        return result.decode().strip()
    except subprocess.CalledProcessError:
        raise RuntimeError(f"[ERROR] Secret not found for: {service_name} in macOS Keychain")
