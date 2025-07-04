import sys
from pathlib import Path

# Add project root to the path to allow importing other tools
sys.path.append(str(Path(__file__).parent.parent))

from tools.repair_engine import run_auto_repair
from tools.validate_flake8 import run_flake8
from tools.validate_imports import get_invalid_imports
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
    else:
        print("Unknown command. Available commands: fix <file>, validate, voice")

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
