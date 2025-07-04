import pytest
from core.agent_router import route_prompt


def test_fredfix_routing():
    """Placeholder docstring for test_fredfix_routing."""
    resp = route_prompt("fredfix", "Test prompt")
    assert resp is not None


def test_chatterfix_routing():
    """Placeholder docstring for test_chatterfix_routing."""
    resp = route_prompt("chatterfix", "Test prompt")
    assert resp is not None


def test_invalid_agent():
    """Placeholder docstring for test_invalid_agent."""
    with pytest.raises(ValueError):
        route_prompt("notarealagent", "Test prompt")


def test_context_passed():
    """Placeholder docstring for test_context_passed."""
    context = {"user": "test", "tags": ["foo"]}
    resp = route_prompt("fredfix", "Test with context", context=context)
    assert resp is not None
