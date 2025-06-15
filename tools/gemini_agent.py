# tools/gemini_agent.py
import os
import google.generativeai as genai
from datetime import datetime
import traceback
import difflib
import shutil

# Load API key from environment or secret manager
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-fallback-key")
genai.configure(api_key=GEMINI_API_KEY)

def query_model(prompt: str, record_to_memory: bool = False, model_name: str = "gemini-pro") -> str:
    try:
        temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        top_p = float(os.getenv("GEMINI_TOP_P", "0.9"))
        max_tokens = int(os.getenv("GEMINI_MAX_TOKENS", "1024"))
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt, generation_config={
            "temperature": temperature,
            "top_p": top_p,
            "max_output_tokens": max_tokens
        })
        result = response.text.strip()
        if record_to_memory:
            write_to_memory(prompt, result, model_name, temperature, top_p, max_tokens)
        return result
    except Exception as e:
        error_msg = f"Error generating content: {str(e)}\n{traceback.format_exc()}"
        if record_to_memory:
            write_to_memory(prompt, error_msg, model_name, temperature, top_p, max_tokens)
        return error_msg

def write_to_memory(prompt: str, result: str, model_name: str = "gemini-pro", temperature: float = 0.7, top_p: float = 0.9, max_tokens: int = 1024, file_path: str = None, old_content: str = None, new_content: str = None):
    memory_path = os.path.expanduser("~/Desktop/Gringomem/gemini_memory.log")
    os.makedirs(os.path.dirname(memory_path), exist_ok=True)
    with open(memory_path, 'a', encoding='utf-8') as f:
        f.write(f"=== TIMESTAMP === {datetime.now()}\n")
        f.write(f"=== MODEL === {model_name} | TEMPERATURE: {temperature} | TOP_P: {top_p} | MAX_TOKENS: {max_tokens}\n")
        f.write(f"=== PROMPT ===\n{prompt}\n\n=== RESPONSE ===\n{result}\n")
        if file_path:
            f.write(f"=== FILE === {file_path}\n")
        if old_content and new_content:
            diff = difflib.unified_diff(
                old_content.splitlines(),
                new_content.splitlines(),
                fromfile='before',
                tofile='after',
                lineterm=''
            )
            f.write("\n".join(diff))
        f.write("\n\n")
