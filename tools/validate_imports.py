import os
import ast
from collections import defaultdict

EXCLUDE_DIRS = ["node_modules", ".venv", "__pycache__"]

def find_python_files(start_path):
    """Finds all Python files in a directory, excluding specified directories."""
    for root, _, files in os.walk(start_path):
        if any(skip in root for skip in EXCLUDE_DIRS):
            continue
        for file in files:
            if file.endswith(".py"):
                yield os.path.join(root, file)

def get_imports(file_path):
    """Gets all imports from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        yield alias.name
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        yield node.module
        except Exception as e:
            print(f"Could not parse {file_path}: {e}")

def build_dependency_graph(start_path):
    """Builds a dependency graph for a Python project."""
    graph = defaultdict(set)
    for file_path in find_python_files(start_path):
        module_name = os.path.splitext(os.path.relpath(file_path, start_path))[0].replace(os.sep, ".")
        for imp in get_imports(file_path):
            graph[module_name].add(imp)
    return graph

def find_cycles(graph):
    """Finds cycles in a dependency graph."""
    path = set()
    visited = set()
    cycles = []

    def visit(node):
        """Placeholder docstring for visit."""
        if node in visited:
            return
        visited.add(node)
        path.add(node)
        for neighbour in graph.get(node, []):
            if neighbour in path:
                cycles.append(list(path))
            else:
                visit(neighbour)
        path.remove(node)

    for node in graph:
        visit(node)
    return cycles

if __name__ == "__main__":
    project_path = "."
    print(f"Building dependency graph for {project_path}...")
    dependency_graph = build_dependency_graph(project_path)
    
    print("Finding cycles...")
    cycles = find_cycles(dependency_graph)
    
    if cycles:
        print("\n❌ Found circular dependencies:")
        for cycle in cycles:
            print(" -> ".join(cycle))
    else:
        print("\n✅ No circular dependencies found.")

    print("\n--- Checking for syntax errors ---")
    invalid_syntax_files = []
    for file_path in find_python_files(project_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
        except (SyntaxError, IndentationError) as e:
            invalid_syntax_files.append(file_path)
            print(f"❌ Invalid syntax in {file_path}: {e}")
    
    if not invalid_syntax_files:
        print("✅ No syntax errors found.")

def get_invalid_imports():
    """
    Runs the import validation and returns a formatted string of any issues.
    """
    cycles = find_cycles(build_dependency_graph("."))
    if cycles:
        return "❌ Found circular dependencies:\n" + "\n".join([" -> ".join(c) for c in cycles])
    
    invalid_syntax_files = []
    for file_path in find_python_files("."):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                ast.parse(f.read())
        except (SyntaxError, IndentationError) as e:
            invalid_syntax_files.append(f"{file_path}: {e}")

    if invalid_syntax_files:
        return "❌ Found syntax errors:\n" + "\n".join(invalid_syntax_files)
        
    return "✅ No import or syntax errors found."
