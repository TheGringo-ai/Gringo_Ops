import sys
import subprocess

def load_prompt(prompt_path, code_snippet):
    with open(prompt_path, 'r') as f:
        template = f.read()
    return template.replace("{{code}}", code_snippet)

def run_llama(prompt_text):
    cmd = [
        "/Users/fredtaylor/Projects/llama.cpp/build/bin/llama-cli",
        "-m", "/Users/fredtaylor/models/CodeLLaMA/codellama-7b-instruct.Q4_K_M.gguf",
        "-p", prompt_text
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

if __name__ == "__main__":
    prompt_file = sys.argv[1]  # e.g., prompts/fix_python_code.txt
    code_snippet = sys.argv[2]  # path to file containing the code
    with open(code_snippet, 'r') as f:
        code = f.read()
    final_prompt = load_prompt(prompt_file, code)
    run_llama(final_prompt)
