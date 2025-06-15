import os
import sys
import argparse
import glob
from datetime import datetime
from openai import OpenAI
import json
from pathlib import Path


def review_file(target, supervised=False):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")

    client = OpenAI(api_key=api_key)

    if not os.path.exists(target):
        print(f"❌ File not found: {target}")
        return

    print(f"🔍 Reviewing {target} with GPT-4 Turbo...")

    with open(target, "r") as f:
        code = f.read()

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a senior Python code reviewer using GPT-4 Turbo. Be clear and concise."},
                {"role": "user", "content": f"Please review the following code:\n\n{code}"}
            ]
        )
        feedback = response.choices[0].message.content
    except Exception as e:
        print(f"❌ Error during API request: {e}")
        return

    print("✅ GPT-4 Turbo Review:\n")
    print(feedback)

    log_filename = f"gpt_review_{os.path.basename(target)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    should_save = True
    if supervised:
        confirm = input(f"\nWould you like to save this review to {log_filename}? (y/n): ").strip().lower()
        if confirm != "y":
            print("❌ Review not saved.")
            should_save = False
    if should_save:
        with open(log_filename, "w") as log_file:
            log_file.write(feedback)
            print(f"💾 Review saved to {log_filename}")
            append_to_memory("gpt-4-turbo", target, f"Please review the following code:\n\n{code}", feedback)

    # TODO: Add support for Gemini 1.5 Pro review and logging
    if False:
        pass


def append_to_memory(model, file_path, prompt, response):
    memory_path = Path.home() / "Desktop/Gringomem/memory.json"
    memory_path.parent.mkdir(parents=True, exist_ok=True)

    if memory_path.exists():
        with open(memory_path, "r") as mem_file:
            try:
                memory = json.load(mem_file)
            except json.JSONDecodeError:
                memory = []
    else:
        memory = []

    memory.append({
        "timestamp": datetime.now().isoformat(),
        "model": model,
        "file": file_path,
        "prompt": prompt,
        "response": response[:1000]  # truncate to avoid bloating
    })

    with open(memory_path, "w") as mem_file:
        json.dump(memory, mem_file, indent=2)


def review(target="FredFix/core/agent.py", supervised=False):
    # If target is a directory, review all .py files inside (non-recursive)
    if os.path.isdir(target):
        py_files = glob.glob(os.path.join(target, "*.py"))
        if not py_files:
            print(f"❌ No Python files found in folder: {target}")
            return
        for py_file in py_files:
            review_file(py_file, supervised=supervised)
    else:
        review_file(target, supervised=supervised)


def main():
    parser = argparse.ArgumentParser(description="Review Python code using GPT-4.")
    parser.add_argument("target", help="Path to Python file or folder to review")
    parser.add_argument("--supervised", action="store_true", help="Prompt before saving review log")
    args = parser.parse_args()
    review(args.target, supervised=args.supervised)


if __name__ == "__main__":
    main()