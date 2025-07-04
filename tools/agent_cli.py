import difflib
import os
from openai import OpenAI
from tools.config import load_config
from tools.logger import log_markdown
from tools.gemini_agent import query_model as gemini_query
from tools.huggingface_agent import query_model as hf_query
from tools.memory import write_to_memory, save_diff_summary

def autopatch_run(args, provider="openai"):
    """Runs the autopatch agent on the target file."""
    conf = load_config()
    if not args.target:
        # Auto-scan all Python files in root if no target is provided
        for root, _, files in os.walk("."):
            for name in files:
                if name.endswith(".py"):
                    args.target = os.path.join(root, name)
                    autopatch_run(args, provider)
        return

    file_path = args.target or conf["defaults"]["review_target"]
    supervised = args.supervised if args.supervised is not None else True

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return

    updated_code = None
    original_code = None

    if provider == "gemini":
        print(f"🤖 Using Gemini to refactor: {file_path}")
        try:
            with open(file_path, "r") as f:
                original_code = f.read()
            updated_code = gemini_query(original_code)
            # Save change to memory
            metadata = {"file": file_path, "provider": provider}
            write_to_memory(original_code, updated_code, metadata)
        except Exception as e:
            print(f"❌ Error using Gemini provider: {e}")
            return
    elif provider == "huggingface":
        print(f"🤗 Using Hugging Face to refactor: {file_path}")
        try:
            with open(file_path, "r") as f:
                original_code = f.read()
            updated_code = hf_query(original_code)
            # Save change to memory
            metadata = {"file": file_path, "provider": provider}
            write_to_memory(original_code, updated_code, metadata)
        except Exception as e:
            print(f"❌ Error using Hugging Face provider: {e}")
            return
    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY environment variable not set.")
            return
        client = OpenAI(api_key=api_key)

        print(f"🔧 Running AutoPatchBoy on: {file_path}")
        try:
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
            # Save change to memory
            metadata = {"file": file_path, "provider": provider}
            write_to_memory(original_code, updated_code, metadata)
        except Exception as e:
            print(f"❌ Error using OpenAI provider: {e}")
            return
    else:
        print(f"❌ Unsupported provider: {provider}")
        return

    if updated_code is None or original_code is None:
        print("❌ No updated code generated; aborting patch.")
        return

    diff = difflib.unified_diff(
        original_code.splitlines(),
        updated_code.splitlines(),
        fromfile="original",
        tofile="patched",
        lineterm=""
    )
    diff_text = "\n".join(diff)
    print(diff_text)

    if supervised:
        confirm = input("\nApply this patch? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Patch not applied.")
            return

    try:
        with open(file_path, "w") as f:
            f.write(updated_code)
            print("✅ Patch applied.")
    except Exception as e:
        print(f"❌ Failed to write patch to file: {e}")
        return

    # Write a markdown log containing summary, diff, and updated code
    log_content = f"### File Patched: `{file_path}`\n\n"
    log_content += "#### 🧾 Patch Diff:\n\n```diff\n" + diff_text + "\n```\n\n"
    log_content += "#### ✅ Updated Code:\n\n```python\n" + updated_code + "\n```"
    log_markdown("AutoPatchBoy Patch", log_content, log_dir="logs/patches")

    # Write side-by-side diff summary
    try:
        save_diff_summary(original_code, updated_code, file_path, provider)
    except Exception as e:
        print(f"❌ Failed to save diff summary: {e}")

def main():
    """Main function for the autopatch agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Run AutoPatchBoy refactor agent.")
    parser.add_argument("--target", type=str, help="Path to the file to refactor.")
    parser.add_argument("--provider", type=str, default="openai", choices=["openai", "gemini", "huggingface"], help="AI provider to use.")
    parser.add_argument("--supervised", action="store_true", help="Require confirmation before applying patch.")
    parser.add_argument("--go", action="store_true", help="Execute the autopatch run immediately.")

    args = parser.parse_args()

    if args.go:
        autopatch_run(args, provider=args.provider)

if __name__ == "__main__":
    main()
