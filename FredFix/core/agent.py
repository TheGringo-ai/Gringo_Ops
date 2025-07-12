# Import OpenAI (optional) and subprocess for local model execution
import subprocess
# core/memory.py

import json
from pathlib import Path
from datetime import datetime

MEMORY_FILE = Path(__file__).parent / "agent_memory.json"

def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# core/repair_engine.py

def repair_all_code():
    # Placeholder logic — eventually this will lint, test, and auto-fix
    return "🔧 Code repair routine executed (placeholder)."

# core/command_router.py

def execute_command(command: str, memory: dict):
    if command == "hello":
        return "👋 Hello from FredFix!"
    elif command == "status":
        return f"📦 Current memory keys: {list(memory.keys())}"
    else:
        return f"❓ Unknown command: '{command}'"


# core/config.py

class AgentConfig:
    def __init__(self):
        self.agent_name = "FredFix"
        self.openai_model = "gpt-4-turbo"


# --- Agent Implementation ---

class FredFixAgent:
    def __init__(self):
        self.memory = load_memory()
        self.config = AgentConfig()

    def run(self, command: str):
        print(f"[DEBUG] Running command: {command}")
        print(f"[DEBUG] Current memory before execution: {self.memory}")
        try:
            if command == "repair":
                result = repair_all_code()
            else:
                result = execute_command(command, self.memory)

            # Update memory with the command and result
            self.memory.setdefault("history", []).append({
                "command": command,
                "result": result
            })

            save_memory(self.memory)
            memory_line = {
                "timestamp": datetime.utcnow().isoformat(),
                "command": command,
                "result": result
            }
            log_path = Path(__file__).parent / "agent_memory.json"
            with open(log_path, "a") as mem_log:
                mem_log.write(json.dumps(memory_line) + "\n")
            print(f"[DEBUG] Memory after execution: {self.memory}")
            print(f"[DEBUG] Command result: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Exception during command execution: {e}")
            raise

    def run_agent(self, input_text: str, model: str = None):
        # Try running as known command first
        known_result = self.run(input_text)
        if "Unknown command" not in known_result:
            return {
                "mode": "command",
                "output": known_result,
                "timestamp": datetime.utcnow().isoformat()
            }

        # Otherwise, treat as natural language prompt
        try:
            # Try local model with Ollama first
            prompt = f"You are FredFix, an AI assistant.\n\nUser: {input_text}"
            # If model is passed (e.g., "llama2", "codellama"), it overrides the default
            selected_model = model or "mistral"
            result = subprocess.run(["ollama", "run", selected_model], input=prompt, text=True, capture_output=True)
            ai_result = result.stdout.strip()

            # Save to memory
            self.memory.setdefault("history", []).append({
                "command": input_text,
                "result": ai_result
            })
            save_memory(self.memory)

            memory_line = {
                "timestamp": datetime.utcnow().isoformat(),
                "command": input_text,
                "result": ai_result
            }
            log_path = Path(__file__).parent / "agent_memory.json"
            with open(log_path, "a") as mem_log:
                mem_log.write(json.dumps(memory_line) + "\n")

            return {
                "mode": "local_model",
                "output": ai_result,
                "timestamp": memory_line["timestamp"]
            }

        except Exception:
            try:
                # Fallback to OpenAI if local fails
                import openai
                openai.api_key_path = ".openai_key.txt"
                response = openai.ChatCompletion.create(
                    model=self.config.openai_model,
                    messages=[
                        {"role": "system", "content": "You are FredFix, an AI assistant."},
                        {"role": "user", "content": input_text}
                    ]
                )
                ai_result = response.choices[0].message.content.strip()

                self.memory.setdefault("history", []).append({
                    "command": input_text,
                    "result": ai_result
                })
                save_memory(self.memory)

                memory_line = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "command": input_text,
                    "result": ai_result
                }
                log_path = Path(__file__).parent / "agent_memory.json"
                with open(log_path, "a") as mem_log:
                    mem_log.write(json.dumps(memory_line) + "\n")

                return {
                    "mode": "openai_fallback",
                    "output": ai_result,
                    "timestamp": memory_line["timestamp"]
                }
            except Exception as fallback_error:
                return {
                    "mode": "error",
                    "error": f"Local and OpenAI failed: {fallback_error}",
                    "timestamp": datetime.utcnow().isoformat()
                }


if __name__ == "__main__":
    import sys
    try:
        print("📣 Starting FredFix Agent...")
        agent = FredFixAgent()
        print("✅ Agent initialized.")

        if len(sys.argv) > 1:
            command = " ".join(sys.argv[1:])
        else:
            command = input("Enter command for FredFix: ")

        print(f"▶️ Running command: {command}")
        output = agent.run(command)
        print(f"\n✅ FredFix Agent Output:\n{output}")

    except Exception as e:
        print(f"❌ FredFix encountered an error: {e}")

# Exportable run_agent function for dashboard use
def run_agent(input_text: str, model: str = None):
    return FredFixAgent().run_agent(input_text, model)

__all__ = ["FredFixAgent", "run_agent"]