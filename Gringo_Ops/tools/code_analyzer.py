import os
import ast
from pathlib import Path
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# This is a placeholder for a real LLM call.
# In a real implementation, this would interact with an API (OpenAI, Gemini, etc.)
# For this example, we'll simulate it by checking for simple anti-patterns.
def get_ai_review(file_path, file_content):
    """
    Simulates an AI model reviewing a file for potential issues.

    Args:
        file_path (str): The path to the file being analyzed.
        file_content (str): The content of the file.

    Returns:
        list: A list of strings, where each string is a potential issue.
    """
    issues = []
    file_extension = Path(file_path).suffix

    # Generic checks for all files
    if "TODO:" in file_content or "FIXME:" in file_content:
        issues.append("Found TODO/FIXME comments that may indicate unfinished work.")
    if "temp_key" in file_content or "hardcoded_password" in file_content:
        issues.append("Potential hardcoded credentials found.")

    # Python-specific checks
    if file_extension == '.py':
        if "os.system(" in file_content:
            issues.append("Use of 'os.system' is a potential security risk. Consider 'subprocess' module instead.")
        # A simple check for missing docstrings in functions
        for i, line in enumerate(file_content.splitlines()):
            if line.strip().startswith("def ") and (i == 0 or not file_content.splitlines()[i-1].strip().startswith('#')):
                 if (i + 1 < len(file_content.splitlines())) and not file_content.splitlines()[i+1].strip().startswith('"""'):
                    issues.append(f"Function '{line.strip().split('(')[0][4:]}' at line {i+1} appears to be missing a docstring.")

    # YAML-specific checks for deployment files
    if file_extension in ['.yaml', '.yml']:
        if "latest" in file_content:
            issues.append("Use of 'latest' tag for container images is discouraged in production environments.")
        if "aws_access_key_id" in file_content or "gcp_secret" in file_content:
             issues.append("Potential cloud credentials found in a config file. Use a secrets manager.")

    return issues

class CodeAnalyzer:
    """
    Analyzes a list of files for potential issues like missing docstrings,
    security vulnerabilities, and other anti-patterns.
    """
    def __init__(self, file_paths, memory=None):
        """
        Initializes the CodeAnalyzer.

        Args:
            file_paths (list): A list of absolute paths to the files to analyze.
            memory (AgentMemory, optional): The agent's memory. Defaults to None.
        """
        self.file_paths = file_paths
        self.memory = memory
        self.report = {}

    def run_analysis(self):
        """
        Runs the analysis on all files and returns a report.
        """
        print("\n[Code Analyzer] Starting analysis...")
        error_files = self.memory.get_error_files() if self.memory else []

        for file_path in self.file_paths:
            if file_path in error_files:
                logger.info(f"[Memory] Skipping file with previous errors: {file_path}")
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                issues = []
                if file_path.endswith('.py'):
                    issues.extend(self._analyze_python_file(file_path, content))
                elif file_path.endswith(('.yaml', '.yml')):
                    issues.extend(self._analyze_yaml_file(content))
                
                # Generic checks for all file types
                issues.extend(self._check_for_todos(content))
                issues.extend(self._check_for_hardcoded_secrets(content))

                if issues:
                    self.report[file_path] = issues
                    print(f"  - Found {len(issues)} potential issues in {Path(file_path).name}")

            except (UnicodeDecodeError, FileNotFoundError) as e:
                print(f"  - Error analyzing {file_path}: {e}")
                if self.memory:
                    self.memory.add_error_file(file_path)
        
        print("[Code Analyzer] Analysis complete.")
        return self.report

    def _analyze_python_file(self, file_path, content):
        """
        Analyzes a single Python file for issues.
        """
        issues = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        issues.append({
                            "description": f"Function or class '{node.name}' appears to be missing a docstring.",
                            "type": "missing_docstring",
                            "line_number": node.lineno,
                            "item_name": node.name
                        })
            # Check for `os.system` usage
            if 'os.system' in content:
                issues.append({
                    "description": "Use of 'os.system' is a potential security risk. Consider 'subprocess' module instead.",
                    "type": "security_risk",
                    "line_number": None, # Could be improved to find the line
                    "item_name": "os.system"
                })
        except SyntaxError as e:
            issues.append({
                "description": f"Invalid Python syntax: {e}",
                "type": "syntax_error",
                "line_number": e.lineno,
                "item_name": None
            })
            if self.memory:
                self.memory.add_error_file(file_path)
        return issues

    def _analyze_yaml_file(self, content):
        """
        Analyzes a single YAML file for issues.
        """
        issues = []
        if 'image: latest' in content or ':latest' in content:
            issues.append({
                "description": "Use of 'latest' tag for container images is discouraged in production environments.",
                "type": "best_practice",
                "line_number": None, # Could be improved to find the line
                "item_name": "latest tag"
            })
        return issues

    def _check_for_todos(self, content):
        """
        Checks for TODO or FIXME comments in the file content.
        """
        issues = []
        if 'TODO' in content or 'FIXME' in content:
            issues.append({
                "description": "Found TODO/FIXME comments that may indicate unfinished work.",
                "type": "todo_comment",
                "line_number": None, # Could be improved
                "item_name": "TODO/FIXME"
            })
        return issues

    def _check_for_hardcoded_secrets(self, content):
        """
        A simple check for hardcoded secrets. This should be replaced with a more robust tool.
        """
        issues = []
        # This is a very basic check and will have false positives.
        if 'key' in content.lower() and ('=' in content or ':' in content):
            # A more sophisticated check would look for high-entropy strings.
            pass # Disabling for now to reduce noise
        return issues

    def save_report(self, report_path):
        """
        Saves the analysis report to a JSON file.
        """
        report_path = Path(report_path)
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=4)
            print(f"\n[Code Analyzer] Analysis report saved to {report_path}")
        except IOError as e:
            print(f"\n[Code Analyzer] Error saving report: {e}")
