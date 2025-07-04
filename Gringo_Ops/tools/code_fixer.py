import ast
from pathlib import Path
import logging
import openai
import os

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

class CodeFixer:
    """
    Generates suggested code fixes for issues identified in a report.
    """
    def __init__(self, report):
        """
        Initializes the CodeFixer with an analysis report.

        Args:
            report (dict): The analysis report generated by CodeAnalyzer.
        """
        self.report = report
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def generate_fixes(self):
        """
        Parses the report and generates a dictionary of proposed fixes.

        Returns:
            dict: A dictionary where keys are file paths and values are lists of fix objects.
        """
        fixes = {}
        for file_path, issues in self.report.items():
            if not Path(file_path).exists() or not file_path.endswith('.py'):
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                tree = ast.parse(source_code)
            except (SyntaxError, UnicodeDecodeError) as e:
                logger.error(f"Skipping file due to parsing error: {file_path} - {e}")
                continue

            file_fixes = []
            for issue in issues:
                issue_type = issue.get('type')
                if issue_type == 'missing_docstring':
                    fix = self._generate_docstring_fix(file_path, issue, source_code, tree)
                    if fix:
                        file_fixes.append(fix)
                else:
                    # For any other issue, try to get an AI-powered fix
                    fix = self._generate_ai_fix(file_path, issue, source_code)
                    if fix:
                        file_fixes.append(fix)
            
            if file_fixes:
                fixes[file_path] = file_fixes
        
        return fixes

    def _generate_docstring_fix(self, file_path, issue, source_code, tree):
        """
        Generates a fix for a missing docstring issue using AST.
        This ensures that the docstring is inserted correctly without breaking the code.
        """
        item_name = issue.get('item_name')
        if not item_name:
            logger.warning(f"Could not find item name in issue: {issue} in {file_path}")
            return None

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == item_name:
                # Check if a docstring already exists. If so, skip.
                if ast.get_docstring(node):
                    continue

                # Find the precise line where the function/class definition ends.
                # This is where the docstring should be inserted.
                if node.body:
                    # Get the line number of the first statement in the body
                    insertion_line = node.body[0].lineno
                    # Get the indentation of the first line of the function body
                    lines = source_code.splitlines()
                    first_line_of_body = lines[node.body[0].lineno - 1]
                    indentation = len(first_line_of_body) - len(first_line_of_body.lstrip())
                else:
                    # If the function has no body (e.g., just `pass`), find the line after the def
                    insertion_line = node.lineno + 1
                    # Get indentation from the `def` line and add 4 spaces
                    lines = source_code.splitlines()
                    def_line = lines[node.lineno - 1]
                    indentation = (len(def_line) - len(def_line.lstrip())) + 4


                # Create the placeholder docstring with the correct indentation.
                docstring_indent = ' ' * indentation
                placeholder_docstring = f'{docstring_indent}"""Placeholder docstring for {item_name}."""'

                return {
                    "line_number": insertion_line,
                    "original_code": "", # Not replacing, just inserting
                    "new_code": placeholder_docstring,
                    "type": "INSERT_BEFORE", # Insert before the first line of the body
                    "original_issue": issue['description']
                }
        
        logger.warning(f"Could not find AST node for '{item_name}' in {file_path}")
        return None

    def _generate_ai_fix(self, file_path, issue, source_code):
        """
        Generates a fix for an issue using the OpenAI API.
        """
        try:
            prompt = self._create_ai_fix_prompt(file_path, issue, source_code)
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Python developer. Your task is to fix the following code. Only return the corrected code, without any explanations or pleasantries."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            fixed_code = response.choices[0].message.content.strip()
            
            return {
                "line_number": 1, # Replace the whole file for now
                "original_code": source_code,
                "new_code": fixed_code,
                "type": "REPLACE_ALL",
                "original_issue": issue['description']
            }
            
        except Exception as e:
            logger.error(f"Failed to get AI fix for {file_path}: {e}")
            return None

    def _create_ai_fix_prompt(self, file_path, issue, source_code):
        """
        Creates the prompt for the AI to fix the code.
        """
        return f"""
        File: {file_path}
        Issue: {issue['description']}
        
        Original Code:
        ---
        {source_code}
        ---
        
        Please provide the corrected code.
        """
