import subprocess
from voice_agent import listen_for_command
def run_and_repair_script(path):
    print(f"🧪 Running: {path}")
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        try:
            output = subprocess.check_output(["python3", path], stderr=subprocess.STDOUT)
            print("✅ Script ran successfully.")
            print(output.decode())
            return
        except subprocess.CalledProcessError as e:
            attempts += 1
            print(f"❌ Error in attempt {attempts}:")
            print(e.output.decode())
            print("🔧 Attempting repair...")

            with open(path, "r") as f:
                original_code = f.read()

            prompt = f"""You're fixing a broken Python script. Here's the code:\n\n{original_code}\n\nAnd here's the error:\n{e.output.decode()}\n\nFix the script so it runs successfully, preserving all original intent and functionality."""
            suggestion = ask_both_models(prompt)

            if not suggestion or suggestion.strip() == original_code.strip():
                print("⚠️ No usable fix suggested. Stopping.")
                break

            with open(path, "w") as f:
                f.write(suggestion)
            print("🔁 Retesting...")
def full_project_review(base_path):
    print(f"🔍 Reviewing project at: {base_path}")
    missing = []

    for root, _, files in os.walk(base_path):
        for name in files:
            path = os.path.join(root, name)
            rel_path = os.path.relpath(path, base_path)

            if name.startswith('.') or name.endswith(('.png', '.jpg', '.gif')):
                continue

            if os.path.getsize(path) == 0 or name.lower() in ['demo.py', 'placeholder.py']:
                confirm = input(f"🗑️ Remove dummy file {rel_path}? (y/n): ").lower()
                if confirm == 'y':
                    os.remove(path)
                    print(f"❌ Deleted: {rel_path}")
                continue

            with open(path, "r", errors="ignore") as f:
                content = f.read()

            new_version = ask_both_models(content)
            if new_version and new_version.strip() != content.strip():
                confirm = input(f"✍️ Update {rel_path}? (y/n): ").lower()
                if confirm == 'y':
                    with open(path, "w") as f:
                        f.write(new_version)
                    print(f"✅ Updated: {rel_path}")

    # Check for essential files
    for required in ["Dockerfile", "README.md", ".env.example", "requirements.txt", "pyproject.toml", ".gitignore"]:
        file_path = os.path.join(base_path, required)
        if not os.path.exists(file_path):
            missing.append(required)

    for item in missing:
        print(f"📄 Missing: {item}")
        prompt = f"Create a production-ready {item} for a Python app that may deploy to Google Cloud, AWS, or Microsoft 365 environments. Include best practices."
        suggestion = ask_both_models(prompt)
        confirm = input(f"💾 Generate {item}? (y/n): ").lower()
        if confirm == 'y':
            with open(os.path.join(base_path, item), "w") as f:
                f.write(suggestion)
            print(f"✅ Created: {item}")
#!/usr/bin/env python3
import sys
import google.generativeai as genai
import openai
from keychain import get_key
import os

sys.path.append('../lib')

# Load keys
openai.api_key = get_key("OPENAI_API_KEY")
genai.configure(api_key=get_key("GEMINI_API_KEY"))

# Gemini model
gemini = genai.GenerativeModel("gemini-1.5-flash")

def ask_both_models(prompt):
    openai_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message["content"]

    gemini_response = gemini.generate_content(prompt).text

    print("\n📦 OpenAI suggestion:\n", openai_response)
    print("\n🔷 Gemini suggestion:\n", gemini_response)

    if openai_response.strip() == gemini_response.strip():
        print("✅ Both models agree. Proceeding with patch.")
        return openai_response
    else:
        print("⚠️ Models disagree. You are the man in the middle.")
        decision = input("Use (o)penai, (g)emini, or (s)kip? ").lower()
        if decision == "o":
            return openai_response
        elif decision == "g":
            return gemini_response
        else:
            print("⏭️ Skipping file.")
            return None

def run_agent():
    print("🤖 FredFix Hybrid Agent ready. Type 'exit' to quit.")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            break
        oai, gem = ask_both_models(user_input)
        print("\n📦 OpenAI:\n", oai)
        print("\n🔷 Gemini:\n", gem)

def patch_file_with_rewrite(file_path):
    with open(file_path, "r") as f:
        original_code = f.read()

    rewritten_code = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a senior developer. Rewrite and optimize this Python code to improve structure, performance, and readability. Preserve all functionality."},
            {"role": "user", "content": original_code}
        ]
    ).choices[0].message["content"]

    with open(file_path, "w") as f:
        f.write(rewritten_code)

    print(f"✅ File '{file_path}' has been auto-patched.")


def check_endpoints(frontend_code, backend_code):
    frontend_lines = frontend_code.splitlines()
    backend_lines = backend_code.splitlines()
    found = []

    for line in frontend_lines:
        if 'fetch(' in line or 'axios' in line:
            for bl in backend_lines:
                if any(endpoint in bl for endpoint in line.split('"')):
                    found.append((line.strip(), "✅ Match"))
                    break
            else:
                found.append((line.strip(), "❌ No match"))

    print("\n🔍 Endpoint Check Results:")
    for entry, status in found:
        print(f"{status}: {entry}")

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                print(f"\n📂 Reviewing: {path}")
                with open(path, "r") as f:
                    code = f.read()
                new_code = ask_both_models(code)
                if new_code:
                    with open(path, "w") as f:
                        f.write(new_code)
                    print(f"✅ Patched: {path}")

if __name__ == "__main__":
    # This script responds to natural language commands directly, e.g.:
    # agent rewrite file at myfile.py
    # agent check between frontend.js and backend.py
    # agent scan folder src/
    # No need to use python or .py syntax.

    def extract_path_from(text, keyword):
        try:
            return text.split(keyword)[1].strip().split()[0]
        except IndexError:
            return None

    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:]).lower()

        if "rewrite" in cmd and "file" in cmd:
            path = extract_path_from(cmd, "at")
            if path and os.path.isfile(path):
                patch_file_with_rewrite(path)
            else:
                print("❌ Couldn't find file path.")

        elif "check" in cmd and "between" in cmd:
            parts = cmd.split("between")[1].split("and")
            if len(parts) == 2:
                front = parts[0].strip()
                back = parts[1].strip()
                if os.path.exists(front) and os.path.exists(back):
                    with open(front) as f1, open(back) as f2:
                        check_endpoints(f1.read(), f2.read())
                else:
                    print("❌ One of the paths doesn't exist.")
            else:
                print("❌ Could not parse front/back paths.")

        elif "scan folder" in cmd:
            path = extract_path_from(cmd, "folder")
            if path and os.path.isdir(path):
                process_directory(path)
            else:
                print("❌ Couldn't find folder path.")

        elif "review my project" in cmd or "clean my folder" in cmd:
            full_project_review(os.getcwd())

        elif "run and repair" in cmd:
            path = extract_path_from(cmd, "repair")
            if path and os.path.isfile(path):
                run_and_repair_script(path)
            else:
                print("❌ Could not locate file to repair.")

        elif "voice mode" in cmd:
            print("🎙️ Voice mode activated. Say your command...")
            while True:
                command = listen_for_command()
                if command.strip().lower() == "exit":
                    break
                print(f"🗣️ Heard: {command}")
                sys.argv = ["agent"] + command.strip().split()
                exec(open(__file__).read())
                break  # Prevent recursive loop

        else:
            print("🤔 Unrecognized command. Launching interactive mode.")
            run_agent()
    else:
        run_agent()