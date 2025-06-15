import subprocess
import os

def get_key(service: str) -> str:
    result = subprocess.run(
        ['security', 'find-generic-password', '-s', service, '-w'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode == 0:
        return result.stdout.strip()

    # Fallback to environment variable
    env_value = os.getenv(service)
    if env_value:
        print(f"⚠️ Using .env fallback for {service}")
        return env_value.strip()

    raise RuntimeError(f"❌ Failed to load {service}")

# Securely load keys without exposing them
KEYS = {}
for name in ["OPENAI_API_KEY", "GEMINI_API_KEY", "HUGGINGFACE_API_KEY", "GITHUB_API_KEY"]:
    try:
        KEYS[name] = get_key(name)
        print(f"✅ {name} loaded")
    except Exception as e:
        print(str(e))
