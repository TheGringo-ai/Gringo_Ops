import os
import json
from datetime import datetime
from huggingface_hub import InferenceClient
from google.cloud import secretmanager

PROJECT_ID = "chatterfix-ui"
MODEL_ID = "meta-llama/Llama-3.1-8B-Instruct"  # Updated model

MAX_TOKENS = int(os.getenv("HF_MAX_TOKENS", "512"))
TEMPERATURE = float(os.getenv("HF_TEMPERATURE", "0.4"))
TOP_P = float(os.getenv("HF_TOP_P", "0.9"))

def get_secret(secret_id: str) -> str:
    """Retrieves a secret from Google Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")

def ask_huggingface(prompt: str, model_id: str = MODEL_ID, max_tokens: int = MAX_TOKENS, temperature: float = TEMPERATURE, top_p: float = TOP_P) -> str:
    """Queries the Hugging Face Inference API."""
    token = get_secret("huggingface-api-key")
    client = InferenceClient(token=token)

    response = client.text_generation(
        prompt,
        model=model_id,
        max_new_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
    )
    return response


if __name__ == "__main__":
    task = "Write a bash script that monitors CPU usage and logs high usage to a file."
    max_tokens = MAX_TOKENS
    temperature = TEMPERATURE
    top_p = TOP_P
    response = ask_huggingface(task, max_tokens=max_tokens, temperature=temperature, top_p=top_p)

    memory_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL_ID,
        "task": task,
        "params": {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p
        },
        "response": response
    }

    memory_path = os.path.expanduser("~/Desktop/Gringomem/memory.json")
    os.makedirs(os.path.dirname(memory_path), exist_ok=True)

    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            memory = json.load(f)
    else:
        memory = []

    memory.append(memory_entry)

    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

    # Create logs directory
    logs_dir = os.path.expanduser("~/Desktop/Gringomem/logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Generate timestamp for log filename
    log_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file_path = os.path.join(logs_dir, f"hf_log_{log_timestamp}.txt")

    # Prepare log content
    log_content = (
        f"Timestamp: {memory_entry['timestamp']}\n"
        f"Model: {MODEL_ID}\n"
        f"Task Prompt: {task}\n"
        f"Parameters:\n"
        f"  max_tokens: {max_tokens}\n"
        f"  temperature: {temperature}\n"
        f"  top_p: {top_p}\n\n"
        f"Raw Output Response:\n{response}\n"
    )

    # Write log file
    with open(log_file_path, "w", encoding="utf-8") as log_file:
        log_file.write(log_content)
