"""
This file makes the FredFix directory runnable as a package.

To run the agent, execute the following command from the project root:
python -m FredFix "your command here"
"""

import sys
from FredFix.core.agent import FredFixAgent

def main():
    """The main entry point for the FredFix agent."""
    # Check if a command was provided as a command-line argument
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
    else:
        # If not, prompt the user for input
        try:
            command = input("Enter command for FredFix agent: ")
        except EOFError:
            # Handle cases where input stream is closed (e.g., in a script)
            command = ""

    if not command.strip():
        print("No command provided. Exiting.")
        return

    # Instantiate and run the agent
    agent = FredFixAgent()
    result = agent.run(command)

    # Print the result
    print(result)

if __name__ == "__main__":
    main()
