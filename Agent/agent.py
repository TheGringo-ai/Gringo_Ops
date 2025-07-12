import os
import subprocess
from rich.prompt import Prompt
from .config import COMMANDS_DIR, log, USE_OPENAI, USE_LLAMA, USE_MISTRAL

def summarize_all_commands():
    for script_path in COMMANDS_DIR.glob("*.py"):
        cmd = script_path.stem
        if not script_path.name.endswith(".py"):
            continue
        with open(script_path, "r") as f:
            code = f.read()
        try:
            if USE_MISTRAL:
                result = subprocess.run(
                    ["ollama", "run", "mistral"],
                    input=f"Summarize this Python script in 2 sentences:\n\n{code}",
                    text=True,
                    capture_output=True
                )
            elif USE_LLAMA:
                result = subprocess.run(
                    ["ollama", "run", "llama2"],
                    input=f"Summarize this Python script in 2 sentences:\n\n{code}",
                    text=True,
                    capture_output=True
                )
            elif USE_OPENAI and os.getenv("OPENAI_API_KEY"):
                result = subprocess.run(
                    ["openai", "api", "chat", "completions.create", "--model", "gpt-4", "--input", code],
                    capture_output=True,
                    text=True
                )
            else:
                raise RuntimeError("No valid model configuration detected.")
            summary = result.stdout.strip()
            print(f"\n[bold green]Summary of '{cmd}':[/bold green]\n{summary}")
            log(f"Summary of {cmd}: {summary}")
        except Exception as e:
            print(f"[red]Failed to summarize {cmd}: {e}[/red]")