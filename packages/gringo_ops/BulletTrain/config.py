import subprocess

def get_key(service: str) -> str:

    """Placeholder docstring for get_key."""    result = subprocess.run(
        ['security', 'find-generic-password', '-s', service, '-w'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"❌ Failed to load {service}: {result.stderr.strip()}")
    return result.stdout.strip()

OPENAI_API_KEY = get_key("OPENAI_API_KEY")
GEMINI_API_KEY = get_key("GEMINI_API_KEY")
HUGGINGFACE_API_KEY = get_key("HUGGINGFACE_API_KEY")
GITHUB_API_KEY = get_key("GITHUB_API_KEY")

print("✅ API keys loaded from macOS Keychain.")
