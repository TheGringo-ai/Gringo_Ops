import subprocess
import os
import yaml

def get_key(service: str) -> str:
    """Placeholder docstring for get_key."""
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

def load_user_config(config_path="gringoops_config.yaml") -> dict:
    """Placeholder docstring for load_user_config."""
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            try:
                return yaml.safe_load(file)
            except yaml.YAMLError as e:
                print(f"❌ Error loading YAML config: {e}")
    else:
        print("⚠️ No gringoops_config.yaml found, using defaults.")
    return {}

USER_CONFIG = load_user_config()
