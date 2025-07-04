# Import OpenAI and set API key
import openai
import os
import json
from datetime import datetime

from .memory import load_memory, save_memory
from .repair_engine import repair_all_code
from .command_router import execute_command
from .config import AgentConfig

openai.api_key = os.environ.get("OPENAI_API_KEY")

class FredFixAgent:
    """The main agent class for FredFix."""
    def __init__(self):
        self.memory = load_memory()
        self.config = AgentConfig()

    def run(self, command: str):
        """Runs a command and returns the result."""
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
            # This should probably be a real logger, but for now...
            with open("Agent/memory.json", "a") as mem_log:
                mem_log.write(json.dumps(memory_line) + "\n")
            print(f"[DEBUG] Memory after execution: {self.memory}")
            print(f"[DEBUG] Command result: {result}")
            return result
        except Exception as e:
            print(f"[ERROR] Exception during command execution: {e}")
            raise

    def run_agent(self, input_text: str):
        """Runs the agent with either a known command or a natural language prompt."""
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
            response = openai.ChatCompletion.create(
                model=self.config.openai_model,
                messages=[
                    {"role": "system", "content": "You are FredFix, an AI assistant."},
                    {"role": "user", "content": input_text}
                ]
            )
            ai_result = response.choices[0].message.content.strip()

            # Save to memory
            self.memory.setdefault("history", []).append({
                "command": input_text,
                "result": ai_result
            })
            save_memory(self.memory)

            # Log JSONL entry
            memory_line = {
                "timestamp": datetime.utcnow().isoformat(),
                "command": input_text,
                "result": ai_result
            }
            with open("Agent/memory.json", "a") as mem_log:
                mem_log.write(json.dumps(memory_line) + "\n")

            return {
                "mode": "ai_prompt",
                "output": ai_result,
                "timestamp": memory_line["timestamp"]
            }

        except Exception as e:
            return {
                "mode": "error",
                "error": str(e),
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
