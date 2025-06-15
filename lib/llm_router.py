import os
import time
from keychain import get_key
from voicestrip import speak_response
import openai.error
import google.api_core.exceptions

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
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.choices[0].message.content.strip()
            token_usage = response.usage if hasattr(response, 'usage') else None
            speak_response(result)
            return {
                "result": result,
                "provider": "openai",
                "model": "gpt-4-turbo",
                "token_usage": token_usage,
                "timestamp": time.time()
            }
        except openai.error.OpenAIError as e:
            return {
                "error": str(e),
                "provider": "openai",
                "model": "gpt-4-turbo",
                "timestamp": time.time()
            }

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        try:
            model = genai.GenerativeModel("gemini-pro")
            response = model.generate_content(prompt)
            result = response.text.strip()
            token_usage = None
            if hasattr(response, 'token_usage'):
                token_usage = response.token_usage
            speak_response(result)
            return {
                "result": result,
                "provider": "gemini",
                "model": "gemini-pro",
                "token_usage": token_usage,
                "timestamp": time.time()
            }
        except google.api_core.exceptions.GoogleAPIError as e:
            return {
                "error": str(e),
                "provider": "gemini",
                "model": "gemini-pro",
                "timestamp": time.time()
            }

    else:
        return {
            "error": "❌ No API key found for OpenAI or Gemini.",
            "timestamp": time.time()
        }

# Example usage
if __name__ == "__main__":
    print(send_prompt("Explain how a gearbox works."))