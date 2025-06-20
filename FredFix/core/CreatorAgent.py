import os
from google.cloud import secretmanager
from datetime import datetime

try:
    import openai
    from openai import OpenAI
    _new_sdk = True
except ImportError:
    _new_sdk = False

class CreatorAgent:
    def __init__(self, model="gpt-4", temperature=0.7, base_path=None):
        self.model = model
        self.temperature = temperature
        self.system_prompt = (
            "You are CreatorAgent, a powerful assistant that writes and updates Python modules "
            "to enhance productivity, automation, and intelligence for the FredFix platform."
        )
        self.base_path = base_path or os.path.dirname(__file__)

        if _new_sdk:
            self.client = OpenAI()
        else:
            self._load_api_key_from_secret_manager()

    def _load_api_key_from_secret_manager(self, secret_id="projects/487771372565/secrets/openai_api_key"):
        client = secretmanager.SecretManagerServiceClient()
        name = f"{secret_id}/versions/latest"
        response = client.access_secret_version(request={"name": name})
        api_key = response.payload.data.decode("UTF-8")
        openai.api_key = api_key

    def create_module(self, prompt):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]

        if _new_sdk:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0].message.content
        else:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            return response.choices[0]['message']['content']

    def save_module(self, filename, content):
        if not filename.endswith(".py"):
            filename += ".py"
        path = os.path.join(self.base_path, filename)
        header = f'"""\nAuto-generated by CreatorAgent on {datetime.now().isoformat()}\nFilename: {filename}\n"""\n\n'
        with open(path, 'w') as f:
            f.write(header + content)
        return path

    def generate_test_stub(self, module_name):
        test_content = (
            f'"""\nTest stub for {module_name}\n"""\n\n'
            f"import unittest\nimport {module_name}\n\n"
            "class TestModule(unittest.TestCase):\n"
            "    def test_placeholder(self):\n"
            f"        self.assertTrue(hasattr({module_name}, '__name__'))\n\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        )
        test_filename = f"test_{module_name}.py"
        return self.save_module(test_filename, test_content)