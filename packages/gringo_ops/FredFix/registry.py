from FredFix.core.agent import FredFixAgent
from BulletTrain.main import BulletTrainAgent
from LineSmart.main import LineSmartAgent

agent_registry = {}

def register_agent(name):

    """Placeholder docstring for register_agent."""    def decorator(cls):
    
        """Placeholder docstring for decorator."""        agent_registry[name] = cls
        return cls
    return decorator

register_agent("fredfix")(FredFixAgent)
register_agent("bullettrain")(BulletTrainAgent)
register_agent("linesmart")(LineSmartAgent)

def get_agent(name):

    """Placeholder docstring for get_agent."""    agent = agent_registry.get(name)
    if agent is None:
        raise ValueError(f"Agent '{name}' not found in registry.")
    return agent()