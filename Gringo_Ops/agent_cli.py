import difflib
import os
from openai import OpenAI
from tools.config import load_config
from tools.logger import log_markdown

def autopatch_run(args):
    conf = load_config()
    file_path = args.target or conf["defaults"]["review_target"]
    supervised = args.supervised if args.supervised is not None else True

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
    client = OpenAI(api_key=api_key)

    print(f"🔧 Running AutoPatchBoy on: {file_path}")
    with open(file_path, "r") as f:
        original_code = f.read()

    response = client.chat.completions.create(
        model=conf["openai"]["model"],
        messages=[
            {"role": "system", "content": "Improve and fix the following Python code:"},
            {"role": "user", "content": original_code}
        ]
    )
    updated_code = response.choices[0].message.content.strip()

    diff = difflib.unified_diff(
        original_code.splitlines(),
        updated_code.splitlines(),
        fromfile="original",
        tofile="patched",
        lineterm=""
    )
    print("\n".join(diff))

    if supervised:
        confirm = input("\nApply this patch? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Patch not applied.")
            return

    with open(file_path, "w") as f:
        f.write(updated_code)
        print("✅ Patch applied.")

    # Write a markdown log containing summary, diff, and updated code
    log_content = f"### File Patched: `{file_path}`\n\n"
    log_content += "#### 🧾 Patch Diff:\n\n```diff\n" + "\n".join(diff) + "\n```\n\n"
    log_content += "#### ✅ Updated Code:\n\n```python\n" + updated_code + "\n```"
    log_markdown("AutoPatchBoy Patch", log_content, log_dir="logs/patches")
