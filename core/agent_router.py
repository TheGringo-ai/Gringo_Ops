# core/agent_router.py

def route_prompt(agent: str, prompt: str, context: dict = None):
    """
    Route a prompt to the correct agent. Add more agents as needed.
    """
    if agent == "fredfix":
        return f"[FredFix] {prompt} (context: {context})"
    elif agent == "chatterfix":
        return f"[ChatterFix] {prompt} (context: {context})"
    else:
        raise ValueError(f"Unknown agent: {agent}")
