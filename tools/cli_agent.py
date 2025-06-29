# -*- coding: utf-8 -*-
"""
Backend logic for the G-Chat Plus CLI tool.
This module uses the centralized LLMRouter to interact with various LLMs.
"""
import sys
import os
from rich.console import Console
from rich.markdown import Markdown

# Add the project root to the Python path to allow imports from `lib`
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from lib.llm_router import LLMRouter, LLMProvider

# --- Agent Personas ---
# A simple dictionary to hold the system prompts for different agent roles.
AGENT_PERSONAS = {
    "default": "You are a helpful, general-purpose AI assistant.",
    "ops": "You are an expert in cloud infrastructure, DevOps, and site reliability engineering. Provide expert advice on deployment, monitoring, and automation. Format outputs as shell commands or configuration files where appropriate.",
    "builder": "You are an expert software architect and senior developer. Provide clean, efficient, and well-documented code. Think step-by-step and provide clear explanations for your design choices.",
    "debugger": "You are a meticulous software debugger. Analyze code snippets, stack traces, and error messages to identify the root cause of issues. Provide clear, concise explanations and suggest concrete fixes.",
    "chatterfix": "You are ChatterFix, an AI assistant specializing in CMMS, ERP, and industrial maintenance. Your expertise covers work orders, asset management, inventory, and predictive maintenance. Provide insights relevant to the ChatterFix application.",
}

def get_llm_router():
    """Initializes and returns an LLMRouter instance."""
    # This could be expanded to pull credentials from a config file
    return LLMRouter()

def run_agent_command(prompt: str, agent: str = "default", model_provider: LLMProvider = "gemini") -> str:
    """
    Runs a single prompt against the specified agent persona and returns the response.
    """
    router = get_llm_router()
    system_prompt = AGENT_PERSONAS.get(agent, AGENT_PERSONAS["default"])
    
    try:
        response = router.get_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=model_provider
        )
        # Print the formatted response to the console
        console = Console()
        console.print(Markdown(response))
        return response
    except Exception as e:
        return f"An error occurred: {e}"

def run_chat_session(agent: str = "default", model_provider: LLMProvider = "gemini"):
    """
    Starts an interactive chat session with the specified agent persona.
    """
    router = get_llm_router()
    system_prompt = AGENT_PERSONAS.get(agent, AGENT_PERSONAS["default"])
    history = []
    console = Console()

    console.print(f"[bold cyan]Starting chat with {agent} agent ({model_provider}). Type 'exit' or 'quit' to end.[/bold cyan]")
    
    while True:
        try:
            prompt = console.input("[bold green]You: [/bold green]")
            if prompt.lower() in ['exit', 'quit']:
                console.print("[bold cyan]Session ended.[/bold cyan]")
                break

            history.append({"role": "user", "content": prompt})
            
            full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

            with console.status("[bold yellow]Thinking...[/bold yellow]") as status:
                response_text = router.get_completion(
                    prompt=full_prompt,
                    system_prompt=system_prompt,
                    provider=model_provider
                )
            
            history.append({"role": "assistant", "content": response_text})
            console.print(f"[bold blue]Agent:[/bold blue]")
            console.print(Markdown(response_text))

        except KeyboardInterrupt:
            console.print("\n[bold cyan]Session ended by user.[/bold cyan]")
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            break
