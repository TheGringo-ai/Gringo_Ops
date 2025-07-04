import os
import json
import subprocess

def prompt_user(prompt, default=None):
    """Prompts the user for input with an optional default value."""
    return input(f"{prompt} [{default}]: ") or default

def run_command(command):
    """Runs a command and checks for errors."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        exit(1)

def onboard():
    """The main onboarding function."""
    print("--- GringoOps Onboarding ---")
    
    # Get user input
    gcp_project_id = prompt_user("Enter your GCP Project ID")
    openai_api_key = prompt_user("Enter your OpenAI API Key")
    firebase_project = prompt_user("Enter your Firebase Project Name", default=gcp_project_id)
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"OPENAI_API_KEY={openai_api_key}\n")
        f.write(f"GCP_PROJECT_ID={gcp_project_id}\n")
        f.write(f"FIREBASE_PROJECT={firebase_project}\n")
        
    # Initialize Firebase
    print("\n--- Initializing Firebase ---")
    run_command(["firebase", "use", "--add", firebase_project])
    
    # Set secrets
    print("\n--- Setting GitHub Secrets ---")
    run_command(["gh", "secret", "set", "GCP_PROJECT_ID", "-b", gcp_project_id])
    run_command(["gh", "secret", "set", "OPENAI_API_KEY", "-b", openai_api_key])
    run_command(["gh", "secret", "set", "FIREBASE_PROJECT", "-b", firebase_project])
    
    print("\n--- Onboarding Complete! ---")
    print("You are now ready to use GringoOps.")

if __name__ == "__main__":
    onboard()
