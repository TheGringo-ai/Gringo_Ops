# core/routes.py

from FredFix.core.agent import repair_agent
from FredFix.core.doc_agent import doc_agent
from FredFix.core.memory import (
    load_memory,
    save_memory,
    search_memory,
    clear_memory,
    summarize_recent,
)
from FredFix.core.voice_agent import voice_agent
from FredFix.core.creator_agent import creator_agent
from FredFix.core.project_manager import project_manager_agent

# Central route dispatcher for FredFix agent logic
AGENT_ROUTES = {
    "repair": repair_agent,
    "docs": doc_agent,
    "load_memory": load_memory,
    "save_memory": save_memory,
    "search_memory": search_memory,
    "clear_memory": clear_memory,
    "summarize_recent": summarize_recent,
    "voice": voice_agent,
    "creator": creator_agent,
    "manager": project_manager_agent,
    "sync_agents": lambda **kwargs: __import__("services").services.sync_agents(**kwargs),
    "run_auto_repair": lambda **kwargs: __import__("services").services.run_auto_repair(**kwargs),
    "transcribe_backlog": lambda **kwargs: __import__("services").services.transcribe_backlog(**kwargs),
    # Add future agents here
}