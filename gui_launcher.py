import os
import tkinter as tk
import subprocess

# 🔇 Suppress Apple Tkinter warning
os.environ["TK_SILENCE_DEPRECATION"] = "1"

PROJECTS = {
    "LineSmart": "~/Projects/GringoOps/LineSmart/main.py",
    "FredFix": "~/Projects/GringoOps/FredFix/main.py",
    "ChatterFix": "~/Projects/GringoOps/ChatterFix/backend/app.py",
    "Agent": "~/Projects/GringoOps/Agent/agent.py"
}

def run_project(name, path):
    expanded_path = os.path.expanduser(path)
    print(f"Launching {name} from {expanded_path}")
    subprocess.Popen(["/usr/bin/python3", "-u", expanded_path])

# ✅ GUI Start
root = tk.Tk()
root.geometry("400x300")
root.title("🚀 Gringo GUI Launcher")

for project, file in PROJECTS.items():
    btn = tk.Button(root, text=f"Launch {project}", width=30, command=lambda f=file, p=project: run_project(p, f))
    btn.pack(pady=10)

# ✅ Status Label
status = tk.Label(root, text="Choose a project to launch.", fg="gray")
status.pack(pady=20)

root.mainloop()
