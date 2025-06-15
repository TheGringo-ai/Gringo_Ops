import os
import openai
import datetime
import re
from tools.memory import write_to_memory
from tools.gemini_agent import query_model as gemini_query
from tools.huggingface_agent import query_model as hf_query

def sanitize_filename(prompt: str) -> str:
    name = re.sub(r'\W+', '_', prompt.strip())[:50]
    return f"{name}.py"

def generate_code(prompt: str, provider="openai", model="gpt-4", temperature=0.7):
    """
    Generate Python code based on the given prompt using selected provider.
    """
    if provider == "openai":
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Generate clean, production-grade Python code."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    elif provider == "gemini":
        return gemini_query(prompt)
    elif provider == "huggingface":
        return hf_query(prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def generate_and_log(prompt: str, provider="openai"):
    code = generate_code(prompt, provider)
    write_to_memory(prompt, code, {"provider": provider})
    return code

def save_code_to_file(code: str, filename: str = None, directory: str = "generated"):
    """
    Save generated code to a file inside the target directory.
    """
    os.makedirs(directory, exist_ok=True)
    filename = filename or sanitize_filename(code[:50])
    filepath = os.path.join(directory, filename)
    with open(filepath, "w") as f:
        f.write(code)
    return filepath

def log_prompt(prompt: str, filename: str, log_path="logs/fredfix_history.log"):
    """
    Log the prompt and the generated filename with a timestamp.
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a") as log_file:
        log_file.write(f"{timestamp} | {filename} | {prompt}\n")