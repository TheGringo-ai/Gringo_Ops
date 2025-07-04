import os
from pathlib import Path

TEMPLATES = {
    "LineSmart": [
        "main.py", "ui.py", "pdf_export.py", "quiz_generator.py",
        "assets/", "data/", "logs/", "README.md", "requirements.txt", ".env.template"
    ],
    "FredFix": [
        "main.py", "core/agent.py", "core/memory.py", "core/routes.py",
        "ui/control.html", "ui/style.css", "README.md", ".env.template"
    ],
    "ChatterFix": [
        "backend/app.py", "backend/database.py", "backend/models.py",
        "frontend/dashboard.py", "frontend/ui_elements.py",
        "firebase/config.json", "README.md", "requirements.txt"
    ],
    "Agent": [
        "agent.py", "memory.json", "config.py", ".env.template", "README.md"
    ]
}

def scaffold(project_root, template_name):
    """Scaffolds a new project from a template."""
    if template_name not in TEMPLATES:
        raise ValueError("❌ Unknown template")

    created = []
    for entry in TEMPLATES[template_name]:
        full_path = Path(project_root) / entry
        if entry.endswith('/'):
            full_path.mkdir(parents=True, exist_ok=True)
        else:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
        created.append(str(full_path))
    
    return created
