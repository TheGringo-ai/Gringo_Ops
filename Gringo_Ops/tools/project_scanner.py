import os
from pathlib import Path

# Default patterns to ignore during file scanning
DEFAULT_IGNORE_PATTERNS = [
    ".git/",
    ".vscode/",
    "__pycache__/",
    ".venv/",
    "node_modules/",
    "dist/",
    "build/",
    "*.pyc",
    "*.log",
]

def get_project_files(root_path, ignore_patterns=None):
    """
    Recursively finds all relevant files in a project directory, ignoring specified patterns.

    Args:
        root_path (str): The root directory of the project to scan.
        ignore_patterns (list, optional): A list of glob patterns to ignore. 
                                          Defaults to DEFAULT_IGNORE_PATTERNS.

    Returns:
        list: A list of absolute file paths.
    """
    if ignore_patterns is None:
        ignore_patterns = DEFAULT_IGNORE_PATTERNS

    root = Path(root_path)
    all_files = {f for f in root.glob("**/*") if f.is_file()}
    
    files_to_ignore = set()
    for pattern in ignore_patterns:
        # Add trailing slash for directories to avoid partial matches on files
        if pattern.endswith('/'):
            files_to_ignore.update(root.glob(f"{pattern}**/*"))
        else:
            files_to_ignore.update(root.glob(f"**/{pattern}"))

    relevant_files = sorted(list(all_files - files_to_ignore))
    print(f"[Project Scanner] Found {len(relevant_files)} relevant files.")
    return [str(f) for f in relevant_files]

if __name__ == '__main__':
    # Example usage: Scan the parent directory of this script
    project_root = Path(__file__).parent.parent.parent
    print(f"Scanning project at: {project_root}")
    files = get_project_files(project_root)
    for file_path in files:
        print(f" - {file_path}")
