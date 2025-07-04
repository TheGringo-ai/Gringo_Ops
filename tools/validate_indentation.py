import ast
import os

def get_indent_violations():
    """
    Finds all Python files in the current directory with indentation errors.
    """
    bad_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".py") and "venv" not in root:
                path = os.path.join(root, file)
                try:
                    with open(path) as f:
                        ast.parse(f.read())
                except (IndentationError, SyntaxError):
                    bad_files.append(path)
    return bad_files

if __name__ == "__main__":
    violations = get_indent_violations()
    if violations:
        print("❌ Found indentation violations in the following files:")
        for file in violations:
            print(f"  - {file}")
    else:
        print("✅ No indentation violations found.")
