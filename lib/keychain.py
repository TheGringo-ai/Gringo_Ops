import os
from dotenv import load_dotenv

# Load .env file for local development. In production (e.g., Streamlit Cloud),
# secrets should be set in the environment or secrets management tool.
load_dotenv()

def get_secret(secret_name: str) -> str:
    """
    Retrieves a secret key from Streamlit secrets, falling back to environment variables.
    This provides a consistent way to manage secrets for both local development
    (using a .env file) and deployment (using Streamlit's secrets management).

    Args:
        secret_name: The name of the secret to retrieve (e.g., "GEMINI_API_KEY").

    Returns:
        The secret value.

    Raises:
        ValueError: If the secret is not found in any of the sources.
    """
    try:
        # First, try Streamlit's secrets management (for deployed apps)
        import streamlit as st
        return st.secrets[secret_name]
    except (ImportError, AttributeError, KeyError):
        # If not in a Streamlit environment or secret not found, try environment variables
        secret_value = os.environ.get(secret_name)
        if secret_value:
            return secret_value
        else:
            raise ValueError(f"Secret '{secret_name}' not found in Streamlit secrets or environment variables.")
