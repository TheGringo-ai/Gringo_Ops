import os
import streamlit as st
from dotenv import load_dotenv

# Load .env file for local development. In production (e.g., Streamlit Cloud),
# secrets should be set in the environment or Streamlit's secrets management.
load_dotenv()

def get_secret(secret_name: str) -> str:
    """
    Retrieves a secret key, prioritizing Streamlit's secrets manager,
    then falling back to environment variables.

    This provides a consistent way to manage secrets for both local development
    (using a .env file) and deployment.

    Args:
        secret_name: The name of the secret to retrieve (e.g., "GEMINI_API_KEY").

    Returns:
        The secret value as a string.

    Raises:
        ValueError: If the secret is not found in any of the sources.
    """
    if hasattr(st, 'secrets') and secret_name in st.secrets:
        return st.secrets[secret_name]
    
    secret_value = os.environ.get(secret_name)
    if secret_value:
        return secret_value
    
    raise ValueError(f"Secret '{secret_name}' not found in Streamlit secrets or environment variables.")