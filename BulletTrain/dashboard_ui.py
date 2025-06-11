import json
from gringoops.llm import OpenAIClient, GeminiClient, HuggingFaceClient

class UnifiedAgent:
    def __init__(self, provider="openai"):
        if provider == "openai":
            self.client = OpenAIClient()
        elif provider == "gemini":
            self.client = GeminiClient()
        elif provider == "huggingface":
            self.client = HuggingFaceClient()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def run_task(self, task, context):
        prompt = self._build_prompt(task, context)
        response = self.client.complete(prompt)
        return self._extract_result(response)

    def _build_prompt(self, task, context):
        return f"Task: {task}\nContext:\n{context}\n\nRespond only with code or final output."

    def _extract_result(self, response):
        # Handles OpenAI-style response with choices
        if isinstance(response, dict) and "choices" in response:
            return response["choices"][0]["message"]["content"]
        return response

import streamlit as st

def main():
    st.set_page_config(page_title="Unified Agent Dashboard", layout="wide")
    st.title("Unified AI Agent")
    st.write("Select your agent and enter a task.")

    provider = st.selectbox("Choose Provider", ["openai", "gemini", "huggingface"])
    task = st.text_input("Task")
    context = st.text_area("Context")

    if st.button("Run"):
        agent = UnifiedAgent(provider=provider)
        result = agent.run_task(task, context)
        st.code(result, language='python')

if __name__ == "__main__":
    main()