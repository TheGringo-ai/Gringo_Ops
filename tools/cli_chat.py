import sys
from pathlib import Path

# Add project root to the path to allow importing other tools
sys.path.append(str(Path(__file__).parent.parent))

from tools.repair_engine import run_auto_repair
from tools.validate_flake8 import run_flake8
from tools.validate_imports import get_invalid_imports
from packages.fredfix.core.test_gen_agent import TestGenAgent
from packages.fredfix.core.voice_agent import listen

def handle_command(command):
    if command.startswith("fix "):
        filepath = command[4:].strip()
        print(run_auto_repair(filepath))
    elif command == "validate":
        print("--- Running flake8 ---")
        print(run_flake8())
        print("\n--- Checking for import/syntax errors ---")
        print(get_invalid_imports())
    elif command.startswith("gentest "):
        parts = command.split(" ")
        if len(parts) != 3:
            print("Usage: gentest <file_path> <function_name>")
            return
        file_path, function_name = parts[1], parts[2]
        agent = TestGenAgent()
        result = agent.generate_tests(file_path, function_name)
        print(result)
    else:
        print("Unknown command. Available commands: fix <file>, validate, gentest <file> <function>")

if __name__ == "__main__":
    print("💬 GringoOps CLI Chat: Type a command or 'exit' to quit.")
    while True:
        try:
            cmd = input("🧠 > ")
            if cmd.lower() in ["exit", "quit"]:
                break
            elif cmd.lower() == "voice":
                print("🎤 Voice mode activated. Speak your command.")
                voice_command = listen()
                if voice_command:
                    print(f"🗣️ You said: {voice_command}")
                    handle_command(voice_command)
            else:
                handle_command(cmd)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
