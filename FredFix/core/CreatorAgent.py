

import os
import openai

class CreatorAgent:
    def __init__(self, model="gpt-4", temperature=0.7):
        self.model = model
        self.temperature = temperature
        self.system_prompt = (
            "You are CreatorAgent, a powerful assistant that writes and updates Python modules "
            "to enhance productivity, automation, and intelligence for the FredFix platform."
        )

    def create_module(self, prompt):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": prompt}
        ]
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature
        )
        return response.choices[0].message['content']

    def save_module(self, filename, content):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'w') as f:
            f.write(content)
        return path