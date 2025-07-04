import os
from openai import OpenAI
import datetime
import re
import sys
import streamlit as st
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.memory import write_to_memory
try:
    from tools.gemini_agent import query_model as gemini_query
except ImportError:
    def gemini_query(prompt):
    
        """Placeholder docstring for gemini_query."""        raise ImportError("tools.gemini_agent or its query_model is missing.")

try:
    from tools.huggingface_agent import query_model as hf_query
except ImportError:
    def hf_query(prompt):
    
        """Placeholder docstring for hf_query."""        raise ImportError("tools.huggingface_agent or its query_model is missing.")

def sanitize_filename(prompt: str) -> str:

    """Placeholder docstring for sanitize_filename."""    name = re.sub(r'\W+', '_', prompt.strip())[:50]
    return f"{name}.py"

def generate_code(prompt: str, provider="openai", model="gpt-4", temperature=0.7):
    """
    Generate Python code based on the given prompt using selected provider.
    """
    if provider == "openai":
        try:
            client = OpenAI()  # Assumes OPENAI_API_KEY is in env
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Generate clean, production-grade Python code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
            )
            code = response.choices[0].message.content.strip()
            if response.usage and hasattr(st, "session_state") and "token_usage" in st.session_state:
                st.session_state.token_usage["prompt"] += response.usage.prompt_tokens
                st.session_state.token_usage["completion"] += response.usage.completion_tokens

            return code
        except Exception as e:
            st.error(f"An error occurred with the OpenAI API: {e}")
            return f"# Error generating code: {e}"
    elif provider == "gemini":
        return gemini_query(prompt)
    elif provider == "huggingface":
        return hf_query(prompt)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def generate_and_log(prompt: str, provider="openai"):

    """Placeholder docstring for generate_and_log."""    code = generate_code(prompt, provider)
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
