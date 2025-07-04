import os
import datetime
from pathlib import Path
from openai import OpenAI
from tools.memory_manager import write_to_memory

# Load OpenAI API key from environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY not found in environment.")

client = OpenAI(api_key=api_key)

def query_model(prompt, model="gpt-4-turbo", temperature=None, max_tokens=None, top_p=None):
    """Queries the OpenAI model with the given prompt."""
    # Use environment variables as fallback if parameters aren't provided
    temperature = temperature or float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    top_p = top_p or float(os.getenv("OPENAI_TOP_P", "0.95"))
    max_tokens = max_tokens or int(os.getenv("OPENAI_MAX_TOKENS", "1024"))

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content
    # Save response to log file
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = Path.home() / "Desktop" / "Gringomem" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"openai_log_{timestamp}.txt"
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(f"🔍 Prompt:\n{prompt}\n\n")
        f.write(f"⚙️ Model: {model}\nTemperature: {temperature}, Top-p: {top_p}, Max tokens: {max_tokens}\n\n")
        f.write(f"🧠 Response:\n{content}\n")
    write_to_memory("openai_agent", {
        "prompt": prompt,
        "response": content,
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens
    })
    return content

if __name__ == "__main__":
    test_prompt = "Summarize the purpose of this application."
    print("🤖 OpenAI Agent Output:\n", query_model(test_prompt))