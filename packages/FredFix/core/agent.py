# Import OpenAI and set API key
import openai
import os
from datetime import datetime

from .memory import load_memory, save_memory
from .repair_engine import repair_all_code
from .command_router import execute_command
from .config import AgentConfig
from tools.export_to_pdf import export_to_pdf

openai.api_key = os.environ.get("OPENAI_API_KEY")

class ChatterBotAgent:
    """The main agent class for ChatterFix."""
    def __init__(self, user_id="default_user"):
        """Initializes the ChatterBotAgent."""
        self.user_id = user_id
        self.memory = load_memory(user_id=self.user_id)
        self.config = AgentConfig()
        self.config.agent_name = "ChatterBot"

    def run(self, command: str):
        """Runs a command and returns the result."""
        print(f"[DEBUG] Running command: {command}")
        print(f"[DEBUG] Current memory before execution: {self.memory}")
        try:
            if command == "repair":
                result = repair_all_code()
            elif command.startswith("export to pdf"):
                text_to_export = command.replace("export to pdf", "").strip()
                result = export_to_pdf(text_to_export)
            else:
                result = execute_command(command, self.memory, self.user_id)

            # Update memory with the command and result
            self.memory.setdefault("history", []).append({
                "command": command,
                "result": result
            })

            save_memory(self.memory, user_id=self.user_id)
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
                    {"role": "system", "content": "You are ChatterBot, an AI assistant for maintenance and operations."},
                    {"role": "user", "content": input_text}
                ]
            )
            ai_result = response.choices[0].message.content.strip()

            # Save to memory
            self.memory.setdefault("history", []).append({
                "command": input_text,
                "result": ai_result
            })
            save_memory(self.memory, user_id=self.user_id)

            return {
                "mode": "ai_prompt",
                "output": ai_result,
                "timestamp": datetime.utcnow().isoformat()
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
        print("📣 Starting ChatterBot Agent...")
        agent = ChatterBotAgent()
        print("✅ Agent initialized.")

        if len(sys.argv) > 1:
            command = " ".join(sys.argv[1:])
        else:
            command = input("Enter command for ChatterBot: ")

        print(f"▶️ Running command: {command}")
        output = agent.run(command)
        print(f"\n✅ ChatterBot Agent Output:\n{output}")

    except Exception as e:
        print(f"❌ ChatterBot encountered an error: {e}")
