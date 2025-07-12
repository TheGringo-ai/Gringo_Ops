import subprocess
import os
import argparse
from pathlib import Path

PROMPT_TEMPLATE = """\
### Instruction:
{instruction}

### Code:
{code}

### Response:
"""

def load_code(filepath):
    with open(filepath, 'r') as f:
        return f.read()

def load_prompt_template(prompt_path):
    with open(prompt_path, 'r') as f:
        return f.read()

def run_llama(prompt):
    llama_bin = "/Users/fredtaylor/Projects/llama.cpp/build/bin/llama-cli"
    model_path = os.getenv("LLAMA_MODEL_PATH")

    if not os.path.exists(llama_bin):
        print(f"Llama binary not found at {llama_bin}")
        return "Llama binary not found."

    if not model_path or not os.path.exists(model_path):
        print("LLAMA_MODEL_PATH is not set or the file doesn't exist.")
        return "Model path not set or not found."

    try:
        print("[INFO] Running LLaMA with low-memory mode")
        result = subprocess.run(
            [
                llama_bin,
                "-m", model_path,
                "--ctx-size", "256",
                "--threads", "2",
                "--temp", "0.7",
                "--top-k", "30",
                "-p", prompt
            ],
            capture_output=True,
            text=True,
            check=True
        )
        print("[DEBUG] LLaMA stdout:\n", result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("[ERROR] LLaMA failed to run")
        print("stdout:\n", e.stdout)
        print("stderr:\n", e.stderr)
        return "Error during LLaMA execution."

def assist(instruction, code_file, prompt_template=None, output_file=None):
    if not os.path.isfile(code_file):
        print(f"[ERROR] Code file '{code_file}' not found.")
        return
    code = load_code(code_file)
    if prompt_template:
        template = load_prompt_template(prompt_template)
    else:
        template = PROMPT_TEMPLATE

    prompt = template.format(instruction=instruction, code=code)
    response = run_llama(prompt)

    # Extract code from response if formatted in a code block
    import re
    code_match = re.search(r"\\begin{code}(.*?)\\end{code}", response, re.DOTALL)
    if code_match:
        cleaned_response = code_match.group(1).strip()
    else:
        cleaned_response = response.strip()

    if output_file:
        with open(output_file, 'w') as f:
            f.write(cleaned_response)
        print(f"Response saved to {output_file}")
    else:
        print(cleaned_response)


# Example usage:
# assist("Fix bugs in this code", "path/to/script.py")

def main():
    parser = argparse.ArgumentParser(description="CodeLLaMA Assistant CLI")
    parser.add_argument("code", help="Path to the code file to assist with")
    parser.add_argument("--instruction", help="Instruction to apply", required=True)
    parser.add_argument("--prompt", help="Path to custom prompt template")
    parser.add_argument("--output", help="Path to save output (default: outputs/output.txt)", default="outputs/output.txt")

    args = parser.parse_args()
    Path("outputs").mkdir(exist_ok=True)
    assist(args.instruction, args.code, args.prompt, args.output)

if __name__ == "__main__":
    main()

# Example usage:
# assist("Fix bugs in this code", "path/to/script.py")