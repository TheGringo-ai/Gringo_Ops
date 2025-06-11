import os
import openai
import ast

def find_all_txt_files(root_dir):
    """Recursively find all .txt files in root_dir and its subdirectories."""
    txt_files = []
    for root, _, files in os.walk(root_dir):
        for file_name in files:
            if file_name.endswith(".txt"):
                txt_files.append(os.path.join(root, file_name))
    return txt_files

import re

def strip_markdown_fences(code: str) -> str:
    """Remove markdown-style content such as code fences, headings, and leftover formatting from content."""
    lines = code.splitlines()
    stripped_lines = []
    for line in lines:
        # Remove triple backticks (any language), markdown headers, and leftover indicators
        if re.match(r"^\s*```", line):
            continue
        if re.match(r"^\s*#+\s", line):  # markdown headings
            continue
        if "Here is the updated code" in line:
            continue
        stripped_lines.append(line)
    return "\n".join(stripped_lines)

def run_cleanup_on_unresolved_tasks(openai_api_key: str, unresolved_dir: str = "UnresolvedTasks", output_dir: str = "CompletedTasks"):
    openai.api_key = openai_api_key

    failed_dir = "FailedCleanup"
    os.makedirs(failed_dir, exist_ok=True)

    # Recursively process all .txt files in unresolved_dir and its subdirectories
    for root, _, files in os.walk(unresolved_dir):
        for file_name in files:
            if file_name.endswith(".txt"):
                unresolved_path = os.path.join(root, file_name)
                with open(unresolved_path, "r") as f:
                    messy_code = f.read()

                print(f"🔧 Cleaning file: {file_name}")

                prompt = (
                    "You are an expert Python developer. Given the following Python file content, rewrite it as clean, complete, executable code. "
                    "In addition to removing markdown, comments, TODOs, and AI review notes, apply any valid suggestions implied or stated in the text. "
                    "These may include adding type hints, improving variable names, refactoring, and making the code more maintainable. "
                    "Return only the final Python code with improvements applied.\n\n"
                    f"{messy_code}"
                )

                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are a Python code cleaner."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.2,
                    )

                    cleaned_code = response["choices"][0]["message"]["content"]
                    cleaned_code = strip_markdown_fences(cleaned_code)

                    try:
                        ast.parse(cleaned_code)
                    except SyntaxError as syntax_err:
                        print(f"❌ Skipping file due to syntax error after cleaning: {file_name} — {syntax_err}")

                        # Save original .txt file to FailedCleanup
                        failed_txt_path = os.path.join(failed_dir, file_name)
                        with open(failed_txt_path, "w") as f:
                            f.write(messy_code)

                        # Write syntax error to log file
                        log_file_name = file_name.replace(".txt", ".log")
                        log_path = os.path.join(failed_dir, log_file_name)
                        with open(log_path, "w") as log_file:
                            log_file.write(f"Syntax error in cleaned code for {file_name}:\n{syntax_err}\n")
                        continue

                    clean_file_name = file_name.replace(".txt", ".py")
                    output_path = os.path.join(output_dir, clean_file_name)

                    with open(output_path, "w") as f:
                        f.write(cleaned_code)

                    print(f"✅ Cleaned and saved: {clean_file_name}")
                except Exception as e:
                    print(f"❌ Failed to clean {file_name}: {e}")

    # Additionally, process all .txt files in the entire project (from root directory)
    project_root = os.path.dirname(os.path.abspath(__file__))
    all_txt_files = find_all_txt_files(project_root)
    for txt_path in all_txt_files:
        # Skip files already processed in unresolved_dir
        if os.path.commonpath([os.path.abspath(txt_path), os.path.abspath(unresolved_dir)]) == os.path.abspath(unresolved_dir):
            continue
        file_name = os.path.basename(txt_path)
        with open(txt_path, "r") as f:
            messy_code = f.read()
        print(f"🔧 Cleaning file: {file_name}")
        prompt = (
            "You are an expert Python developer. Given the following Python file content, rewrite it as clean, complete, executable code. "
            "In addition to removing markdown, comments, TODOs, and AI review notes, apply any valid suggestions implied or stated in the text. "
            "These may include adding type hints, improving variable names, refactoring, and making the code more maintainable. "
            "Return only the final Python code with improvements applied.\n\n"
            f"{messy_code}"
        )
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Python code cleaner."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
            )
            cleaned_code = response["choices"][0]["message"]["content"]
            cleaned_code = strip_markdown_fences(cleaned_code)

            try:
                ast.parse(cleaned_code)
            except SyntaxError as syntax_err:
                print(f"❌ Skipping file due to syntax error after cleaning: {file_name} — {syntax_err}")

                # Save original .txt file to FailedCleanup
                failed_txt_path = os.path.join(failed_dir, file_name)
                with open(failed_txt_path, "w") as f:
                    f.write(messy_code)

                # Write syntax error to log file
                log_file_name = file_name.replace(".txt", ".log")
                log_path = os.path.join(failed_dir, log_file_name)
                with open(log_path, "w") as log_file:
                    log_file.write(f"Syntax error in cleaned code for {file_name}:\n{syntax_err}\n")
                continue

            clean_file_name = file_name.replace(".txt", ".py")
            output_path = os.path.join(output_dir, clean_file_name)
            with open(output_path, "w") as f:
                f.write(cleaned_code)
            print(f"✅ Cleaned and saved: {clean_file_name}")
        except Exception as e:
            print(f"❌ Failed to clean {file_name}: {e}")
if __name__ == "__main__":
    run_cleanup_on_unresolved_tasks(openai_api_key=os.getenv("OPENAI_API_KEY"))