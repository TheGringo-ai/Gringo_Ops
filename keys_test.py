import os

def print_key_status(name, key):
    status = "✅ Found" if key else "❌ Missing"
    masked = f"{key[:4]}...{key[-4:]}" if key else "None"
    print(f"{name}: {status} ({masked})")

def run_key_tests():
    print("\n🔐 Environment API Key Status:\n")
    print_key_status("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY", ""))
    print_key_status("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
    print_key_status("HUGGINGFACE_API_KEY", os.getenv("HUGGINGFACE_API_KEY", ""))
    print_key_status("GITHUB_API_KEY", os.getenv("GITHUB_API_KEY", ""))
    print("\n✅ Key test complete.\n")

if __name__ == "__main__":
    run_key_tests()
