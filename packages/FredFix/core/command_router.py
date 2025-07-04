def execute_command(command: str, memory: dict):
    """Executes a command and returns the result."""
    if command == "hello":
        return "👋 Hello from FredFix!"
    elif command == "status":
        return f"📦 Current memory keys: {list(memory.keys())}"
    elif command.startswith("create work order"):
        task_description = command.replace("create work order", "").strip()
        if not task_description:
            return "Please provide a description for the work order."
        
        # In a real app, this would create a record in a database.
        # For now, we'll just format it nicely.
        return f"""
        **New Work Order Created**
        ---
        **Task:** {task_description}
        **Status:** Open
        **Priority:** Medium (auto-assigned)
        **Assigned To:** Unassigned
        """
    else:
        return f"❓ Unknown command: '{command}'"
