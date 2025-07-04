import os
import google.generativeai as genai

def query_model(prompt="What is the status of project Gemini?"):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY environment variable not set.")
    
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        print("🔍 Gemini Response:\n")
        print(response.text)
    except Exception as e:
        print(f"❌ Failed to get response from Gemini: {e}")
