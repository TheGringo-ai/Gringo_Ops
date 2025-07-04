import subprocess
import os
AUTO_RESOLVE_MODEL = os.getenv("DEFAULT_AI_MODEL", "").lower()

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


# Helper: prompt user to resolve model disagreement
def resolve_conflict(openai_output, gemini_output):
    if AUTO_RESOLVE_MODEL in ['o', 'g']:
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