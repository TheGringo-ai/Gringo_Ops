import os
import tkinter as tk
import subprocess
import json

# 🔇 Suppress Apple Tkinter warning
os.environ["TK_SILENCE_DEPRECATION"] = "1"


# --- Load configuration from tools/launcher_config.json
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "launcher_config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Build PROJECTS and GROUPS dictionaries from the config, preserving group order.
PROJECTS = {}
GROUPS = {}
PROJECT_DESCRIPTIONS = {}
for group in config.get("groups", []):
    group_name = group.get("name")
    GROUPS[group_name] = []
    for proj in group.get("projects", []):
        pname = proj["name"]
        PROJECTS[pname] = proj["path"]
        PROJECT_DESCRIPTIONS[pname] = proj.get("description", f"Click to launch the {pname} project.")
        GROUPS[group_name].append(pname)

def run_project(name, path):
    expanded_path = os.path.expanduser(path)
    print(f"Launching {name} from {expanded_path}")
    if expanded_path.endswith(".py") and "streamlit" in expanded_path.lower():
        subprocess.Popen(["streamlit", "run", expanded_path])
    else:
        subprocess.Popen(["/usr/bin/python3", "-u", expanded_path])
    status.config(text=f"Launching {name}...")

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)

    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(500, self.showtip)

    def unschedule(self):
        id_ = self.id
        self.id = None
        if id_:
            self.widget.after_cancel(id_)

    def showtip(self, event=None):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + cy + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# ✅ GUI Start
root = tk.Tk()
root.geometry("400x300")
root.title("🚀 Gringo GUI Launcher")

group_bg_colors = {
    "Core Tools": "#f0f0f0",
    "Dashboards": "#e8f4f8",
    "Assistants": "#f8f0e8"
}

for group_name, projects in GROUPS.items():
    frame = tk.LabelFrame(root, text=group_name, padx=10, pady=10, bg=group_bg_colors.get(group_name, "#ffffff"))
    frame.pack(fill="x", padx=10, pady=5)
    for project in projects:
        file = PROJECTS[project]
        btn = tk.Button(frame, text=f"Launch {project}", width=30, command=lambda f=file, p=project: run_project(p, f))
        btn.pack(pady=5)
        ToolTip(btn, PROJECT_DESCRIPTIONS.get(project, f"Click to launch the {project} project."))

# ✅ Status Label
status = tk.Label(root, text="Choose a project to launch.", fg="gray")
status.pack(pady=20)

root.mainloop()
