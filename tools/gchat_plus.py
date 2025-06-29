#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# gchat_plus.py - GringoOps CLI Assistant

A powerful, logged, multi-agent command-line interface for interacting with LLMs.

**Features:**
- Interactive chat mode (`--chat`).
- Direct command execution.
- Multiple agent personas (`--agent`).
- All interactions logged to `~/.gchat_log.md`.
- Richly formatted Markdown output.
"""
import argparse
import datetime
import os
import sys
from cli_agent import run_agent_command, run_chat_session

# --- Configuration ---
LOG_FILE = os.path.expanduser("~/.gchat_log.md")

# --- Logging Utility ---
def log_interaction(agent: str, prompt: str, response: str):
    """Appends a record of the interaction to the log file."""
    timestamp = datetime.datetime.now().isoformat()
    try:
        with open(LOG_FILE, "a") as log:
            log.write(f"\n---\n")
            log.write(f"**Timestamp:** `{timestamp}` | **Agent:** `{agent}`\n")
            log.write(f"### Prompt\n"
                      f"```\n"
                      f"{prompt}\n"
                      f"```\n")
            log.write(f"### Response\n"
                      f"{response}\n"
                      f"---\n")
    except IOError as e:
        print(f"Warning: Could not write to log file {LOG_FILE}. Error: {e}")

# --- Main Execution ---
def main():
    """Parses arguments and runs the appropriate function."""
    parser = argparse.ArgumentParser(
        description="🔮 G-Chat Plus: A multi-agent CLI for LLMs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="The prompt to send to the agent. If omitted, starts in chat mode."
    )
    parser.add_argument(
        "--agent",
        default="default",
        choices=['default', 'ops', 'builder', 'debugger', 'chatterfix'],
        help="The agent persona to use."
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Force interactive chat mode, even with a prompt."
    )
    parser.add_argument(
        "--model",
        default="gemini",
        choices=['gemini', 'openai', 'anthropic'],
        help="The underlying LLM provider to use."
    )

    args = parser.parse_args()

    if args.chat or not args.prompt:
        # Start interactive chat session
        run_chat_session(agent=args.agent, model_provider=args.model)
    else:
        # Run a single command
        response = run_agent_command(args.prompt, agent=args.agent, model_provider=args.model)
        # The response is already printed by the function, we just need to log it.
        # Note: The response object itself is the string content.
        log_interaction(args.agent, args.prompt, response)

if __name__ == "__main__":
    main()
