from config import (
    OPENAI_API_KEY,
    GEMINI_API_KEY,
    HUGGINGFACE_API_KEY,
    GITHUB_API_KEY
)

def print_key_status(name, key):
    status = "✅ Found" if key else "❌ Missing"
    masked = f"{key[:4]}...{key[-4:]}" if key else "None"
    print(f"{name}: {status} ({masked})")

def run_key_tests():
    print("\n🔐 Keychain API Key Status:\n")
    print_key_status("OPENAI_API_KEY", OPENAI_API_KEY)
    print_key_status("GEMINI_API_KEY", GEMINI_API_KEY)
    print_key_status("HUGGINGFACE_API_KEY", HUGGINGFACE_API_KEY)
    print_key_status("GITHUB_API_KEY", GITHUB_API_KEY)
    print("\n✅ Key test complete.\n")

if __name__ == "__main__":
    run_key_tests()
