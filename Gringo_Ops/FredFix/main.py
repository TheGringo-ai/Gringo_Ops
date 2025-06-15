
import sys
import os
from keychain import get_key

class FredFixAgent:
    def __init__(self):
        self.api_key = get_key("openai") or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("❌ API key not found. Set it in keychain or environment.")
        print("🔑 API Key loaded successfully.")

    def scan_project(self, root="."):
        py_files = []
        for subdir, _, files in os.walk(root):
            for file in files:
                if file.endswith(".py"):
                    py_files.append(os.path.join(subdir, file))
        return py_files

    def review_file(self, path):
        with open(path, "r") as f:
            content = f.read()

        try:
            import openai
            openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Python code reviewer."},
                    {"role": "user", "content": f"Review and suggest improvements:\n{content}"}
                ]
            )
            print(f"🧠 Review for {path}:\n")
            print(response.choices[0].message["content"])
            # Save AI review to log
            with open("repair_log.txt", "a") as log:
                log.write(f"\n🛠️ Repair for {path}\n")
                log.write(response.choices[0].message["content"] + "\n")
        except Exception as e:
            print(f"❌ Failed to review {path}: {e}")

if __name__ == "__main__":
    agent = FredFixAgent()
    files = agent.scan_project()
    print(f"🧠 FredFix found {len(files)} Python files.")

    for path in files:
        print(f"\n📄 Reviewing: {path}")
        agent.review_file(path)
