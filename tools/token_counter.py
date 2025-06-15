import os
import tiktoken

enc = tiktoken.get_encoding('cl100k_base')
total_tokens = 0
excluded_dirs = {"node_modules", "__pycache__", ".venv", ".git", "build", "dist", ".pytest_cache"}

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in excluded_dirs]
    for file in files:
        if file.endswith((".py", ".md", ".txt", ".json", ".yaml", ".yml")):
            path = os.path.join(root, file)
            try:
                if os.path.getsize(path) < 1_000_000:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        tokens = len(enc.encode(content))
                        total_tokens += tokens
            except Exception:
                pass

print(f"🧠 Estimated total tokens (clean): {total_tokens:,}")
