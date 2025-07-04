import openai
import os
import ast

class TestGenAgent:
    """An agent that generates unit tests for Python functions."""

    def __init__(self):
        """Initializes the TestGenAgent."""
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set.")
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def generate_tests(self, file_path, function_name):
        """
        Generates pytest unit tests for a specific function in a file.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            function_source = self._extract_function_source(source_code, function_name)
            if not function_source:
                return {"error": f"Function '{function_name}' not found in {file_path}."}

            prompt = self._create_test_generation_prompt(function_source)
            
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert Python developer specializing in writing pytest unit tests. Generate a complete, runnable pytest file, including all necessary imports."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            test_code = response.choices[0].message.content.strip()
            
            # Clean up the code block if the model returns it
            if test_code.startswith("```python"):
                test_code = test_code[10:]
            if test_code.endswith("```"):
                test_code = test_code[:-3]

            self._save_tests(file_path, test_code)
            
            return {"success": f"Tests generated for {function_name} in {file_path}."}

        except Exception as e:
            return {"error": f"Failed to generate tests: {e}"}

    def _extract_function_source(self, source_code, function_name):
        """Extracts the source code of a specific function from a file."""
        try:
            tree = ast.parse(source_code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name:
                    return ast.get_source_segment(source_code, node)
            return None
        except SyntaxError:
            return None # Let the main repair loop handle syntax errors

    def _create_test_generation_prompt(self, function_source):
        """Creates the prompt for the AI to generate tests."""
        return f"""
        Please generate a complete pytest unit test file for the following Python function.
        The test file should include all necessary imports and follow best practices.
        Ensure you cover edge cases and provide meaningful assertions.

        Function to test:
        ---
        {function_source}
        ---
        """

    def _save_tests(self, original_file_path, test_code):
        """Saves the generated tests to a new file."""
        test_dir = Path(original_file_path).parent / "tests"
        test_dir.mkdir(exist_ok=True)
        
        original_filename = Path(original_file_path).stem
        test_file_path = test_dir / f"test_{original_filename}.py"
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_code)
        
        print(f"✅ Tests saved to {test_file_path}")

from pathlib import Path
