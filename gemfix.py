import os
import json
from pathlib import Path
from FredFix.core.agent import CreatorAgent
from Agent.memory import save_memory
from tools.gemini_query import gemini_review

PROJECT_ROOT = Path(__file__).parent

def scan_and_review_all():
    reviewed_files = []
    memory_log = []

    for file_path in PROJECT_ROOT.rglob("*"):
        if file_path.suffix not in [".py", ".yml", ".yaml", ".sh", ".txt", ".md", ".json", ".toml", ".dockerignore", ".gitignore", ".env", ""]:
            continue
        if file_path.name in ["gemfix.py", "__init__.py"] or not file_path.is_file():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Could not read {file_path}: {e}")
            continue

        review_prompt = f"""
        You are Gemini. Analyze this Python file for:
        - Broken links or missing references between modules or UI files
        - Incomplete functions or placeholders not shown in the UI
        - Memory and logging integration consistency
        - UI design/navigation consistency if this is a Streamlit file
        - Suggestions for enhancement or structure improvement

        Provide a JSON response:
        {{
            "file": "{file_path.name}",
            "suggestions": [...],
            "fixes": [{{"old": "...", "new": "..."}}]
        }}
        """
        print(f"🔍 Reviewing: {file_path}")
        result = gemini_review(review_prompt)

        if isinstance(result, str):
            print(f"⚠️ Error in review: {result}")
            continue

        try:
            parsed = json.loads(result)
            reviewed_files.append(parsed["file"])
            save_memory("GemFix", f"Audit: {file_path.name}", result)
            apply_fixes(file_path, parsed.get("fixes", []))
            memory_log.append(parsed)
        except Exception as e:
            print(f"❌ Could not parse Gemini output for {file_path}: {e}")

    print(f"✅ Scanned {len(reviewed_files)} files. Memory stored.")
    return memory_log

def apply_fixes(file_path, fixes):
    if not fixes:
        return

    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    for fix in fixes:
        if fix["old"] in code:
            code = code.replace(fix["old"], fix["new"])

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    print(f"🛠 Patched: {file_path.name}")

if __name__ == "__main__":
    scan_and_review_all()
