import os

def print_key_status(name, key):
    """Prints the status of an API key."""
    status = "✅ Found" if key else "❌ Missing"
    masked = f"{key[:4]}...{key[-4:]}" if key else "None"
    print(f"{name}: {status} ({masked})")

def run_key_tests():
    """Runs tests to check for the presence of API keys in the environment."""
    print("\n🔐 Environment API Key Status:\n")
    print_key_status("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    print_key_status("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    print_key_status("HUGGINGFACE_API_KEY", os.getenv("HUGGINGFACE_API_KEY", ""))
    print_key_status("GITHUB_API_KEY", os.getenv("GITHUB_API_KEY", ""))
    print("\n✅ Key test complete.\n")

if __name__ == "__main__":
    run_key_tests()
