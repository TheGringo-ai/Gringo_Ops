import ast
import os

def get_indent_violations():
    """
    Finds all Python files in the current directory with indentation errors.
    """
    bad_files = []
    for root, _, files in os.walk("."):
        for f in files:
            if f.endswith(".py") and "venv" not in root:
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, "r", encoding="utf-8") as src:
                        ast.parse(src.read())
                except IndentationError:
                    bad_files.append(file_path)
                except SyntaxError:
                    # We'll let the import validator handle other syntax errors
                    continue
    return bad_files

if __name__ == "__main__":
    violations = get_indent_violations()
    if violations:
        print("❌ Found indentation violations in the following files:")
        for file in violations:
            print(f"  - {file}")
    else:
        print("✅ No indentation violations found.")
