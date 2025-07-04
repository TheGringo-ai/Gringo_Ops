def execute_command(command: str, memory: dict):
    """Executes a command and returns the result."""
    if command == "hello":
        return "👋 Hello from FredFix!"
    elif command == "status":
        return f"📦 Current memory keys: {list(memory.keys())}"
    else:
        return f"❓ Unknown command: '{command}'"
