import os
import google.generativeai as genai

def query_model(prompt="What is the status of project Gemini?"):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError("GOOGLE_API_KEY environment variable not set.")
    
    genai.configure(api_key=api_key)

    try:
        model = genai.GenerativeModel(
            model_name="models/gemini-1.5-pro",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024
            }
        )
        response = model.generate_content(prompt)
        print("🔍 Gemini Response:\n")
        print(response.text if hasattr(response, "text") else response)
    except Exception as e:
        print(f"❌ Failed to get response from Gemini: {e}")
