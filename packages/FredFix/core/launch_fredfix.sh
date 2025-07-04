# agent_router.py – Shared Router for FredFix and ChatterFix agents
from core.fredfix_agent import FredFixAgent
from core.chatterfix_agent import ChatterFixAgent

AGENT_MAP = {
    "fredfix": FredFixAgent,
    "chatterfix": ChatterFixAgent
}

def route_prompt(agent_name, command, context=None):
    """
    Routes the prompt to the specified agent.
    agent_name: 'fredfix' or 'chatterfix'
    command: str prompt
    context: optional dict for memory, user, tags
    """
    if agent_name not in AGENT_MAP:
        raise ValueError(f"Agent '{agent_name}' not recognized.")

    agent_class = AGENT_MAP[agent_name]()
    return agent_class.run(command, context=context or {})
