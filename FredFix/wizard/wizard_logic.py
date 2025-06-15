"""
wizard_logic.py - Core logic for FredFix's AI-powered code generation wizard.
Handles generation, saving, and logging of AI-created code snippets.
"""

import os
import openai
import datetime

def generate_code(prompt: str, model="gpt-4", temperature=0.7):
    """
    Generate Python code based on the given prompt.
    Placeholder for memory-enhanced context injection (to be implemented).
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "Generate clean, production-grade Python code."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()

def save_code_to_file(code: str, filename: str, directory: str = "generated"):
    """
    Save generated code to a file inside the target directory.
    """
    os.makedirs(directory, exist_ok=True)
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

def load_prompt_history(log_path="logs/fredfix_history.log"):
    """
    Load the previous prompt history from the log file.
    Returns a list of tuples: (timestamp, filename, prompt)
    """
    history = []
    if os.path.exists(log_path):
        with open(log_path, "r") as log_file:
            for line in log_file:
                parts = line.strip().split(" | ")
                if len(parts) == 3:
                    history.append(tuple(parts))
    return history