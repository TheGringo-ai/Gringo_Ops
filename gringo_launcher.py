import os
import sys
import subprocess

# Modify this dictionary to include new projects as needed
PROJECTS = {
    "1": ("LineSmart", "LineSmart/ui.py"),
    "2": ("FredFix", "FredFix/main.py"),
    "3": ("ChatterFix", "ChatterFix/backend/app.py"),
    "4": ("Agent", "Agent/agent.py"),
    "5": ("BulletTrain", "BulletTrain/main.py")
}

def run(command):
    subprocess.run(command, shell=True)

def menu():
    print("\n🧠 GringoOps Project Launcher\n")
    for k, (name, _) in PROJECTS.items():
        print(f" [{k}] {name}")
    print(" [N] New project from template")
    print(" [Q] Quit\n")

def launch(project_key):
    project_name, entry = PROJECTS[project_key]
    path = os.path.expanduser(f"~/Projects/GringoOps/{project_name}")
    venv = os.path.join(path, ".venv")

    print(f"\n🚀 Launching {project_name}...\n")

    if not os.path.exists(venv):
        print("📦 Setting up virtual environment...")
        run(f"cd '{path}' && python3 -m venv .venv && source .venv/bin/activate && touch requirements.txt && pip install -r requirements.txt")

    activate = f"source {venv}/bin/activate"
    if entry.endswith("ui.py"):
        launch = f"streamlit run {path}/{entry}"
    else:
        launch = f"python3 {path}/{entry}"
    os.system(f'''zsh -c '{activate} && {launch}' ''')

def new_project():
    name = input("📛 New project name: ").strip()
    template = input("📦 Template (LineSmart, FredFix, etc.): ").strip()
    scaffold = os.path.expanduser("~/Projects/GringoOps/run_scaffolder.py")
    if not os.path.exists(scaffold):
        print("❌ Missing run_scaffolder.py. Please add it to GringoOps.")
        return
    cmd = f"python3 {scaffold} ~/Projects/GringoOps/{name} {template}"
    run(cmd)
    print("✅ Project created.\n🔁 Restart the launcher to see it listed.")

if __name__ == "__main__":
    while True:
        menu()
        choice = input("❯ ").strip().lower()
        if choice in PROJECTS:
            launch(choice)
        elif choice == 'n':
            new_project()
        elif choice == 'q':
            print("👋 Goodbye.")
            sys.exit()
        else:
            print("❌ Invalid choice.")
