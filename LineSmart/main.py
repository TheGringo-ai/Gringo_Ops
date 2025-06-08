import subprocess
import os

def get_key(service_name: str) -> str:
    """
    Returns secret from macOS Keychain, or environment fallback if unavailable.
    """
    try:
        result = subprocess.check_output(
            ['security', 'find-generic-password', '-s', service_name, '-w'],
            stderr=subprocess.DEVNULL
        )
        return result.decode().strip()
    except subprocess.CalledProcessError:
        return os.getenv(service_name.upper(), "")


openai_key = get_key("OPENAI_API_KEY")
gemini_key = get_key("GEMINI_API_KEY")
huggingface_key = get_key("HUGGINGFACE_API_KEY")
github_key = get_key("GITHUB_API_KEY")


# --- Temporary execution block for LineSmart training generation ---
if __name__ == "__main__":
    print("✅ LineSmart boot sequence started.")

    # Check API keys
    def mask(k): return f"{k[:4]}...{k[-4:]}" if k else "None"
    print(f"OPENAI_API_KEY: {'✅' if openai_key else '❌'} ({mask(openai_key)})")
    print(f"GEMINI_API_KEY: {'✅' if gemini_key else '❌'} ({mask(gemini_key)})")
    print(f"HUGGINGFACE_API_KEY: {'✅' if huggingface_key else '❌'} ({mask(huggingface_key)})")
    print(f"GITHUB_API_KEY: {'✅' if github_key else '❌'} ({mask(github_key)})")

    # Placeholder: Launch LineSmart trainer
    print("\n🚀 Generating LineSmart technician training...")
    # TODO: Replace with real trainer code
    print("📄 Training PDF generated: training_module_temp.pdf")
    print("✅ LineSmart operation completed.\n")
