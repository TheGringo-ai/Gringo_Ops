import os
from keychain import get_key

# Detect which LLM provider to use
OPENAI_KEY = get_key("openai")
GEMINI_KEY = get_key("gemini")

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
        return response.choices[0].message.content.strip()

    elif provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text.strip()

    else:
        return "❌ No API key found for OpenAI or Gemini."

# Example usage
if __name__ == "__main__":
    print(send_prompt("Explain how a gearbox works."))