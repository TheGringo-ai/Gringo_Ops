import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../GringoVoiceStrip')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
# Comment out voicestrip import if not present
# from voicestrip import speak_response
from keychain import get_key

# Detect which LLM provider to use
OPENAI_KEY = get_key("openai")
GEMINI_KEY = get_key("gemini")

# Sends prompt to the selected LLM and optionally speaks the result aloud using Gringo VoiceStrip.
def use_provider():
    if OPENAI_KEY:
        return "openai"
    elif GEMINI_KEY:
        return "gemini"
    else:
        return None

def send_prompt(prompt, model="gpt-4"):
    provider = use_provider()
    if provider == "openai":
        import openai
        openai.api_key = OPENAI_KEY
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip()
        # speak_response(result)
        return result

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        result = response.text.strip()
        # speak_response(result)
        return result

    else:
        return "❌ No API key found for OpenAI or Gemini."

class LLMRouter:
    """Router for LLM providers (OpenAI, Gemini, etc)."""
    def __init__(self):
        self.provider = use_provider()

    def send(self, prompt, model="gpt-4"):
        return send_prompt(prompt, model)

# Example usage
if __name__ == "__main__":
    print(send_prompt("Explain how a gearbox works."))