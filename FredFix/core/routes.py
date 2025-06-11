# routes.py

from FredFix.core.agent import repair_agent
from FredFix.core.doc_agent import doc_agent
from FredFix.core.memory import load_memory, save_memory, search_memory, clear_memory, summarize_recent

# Central route dispatcher for FredFix agent logic
AGENT_ROUTES = {
    "repair": repair_agent,
    "docs": doc_agent,
    "load_memory": load_memory,
    "save_memory": save_memory,
    "search_memory": search_memory,
    "clear_memory": clear_memory,
    "summarize_recent": summarize_recent,
    # Add future agents here
}

def run_agent(agent_name, **kwargs):
    if agent_name in AGENT_ROUTES:
        return AGENT_ROUTES[agent_name](**kwargs)
    else:
        raise ValueError(f"Unknown agent: {agent_name}")