from .settings_context import SettingsContext
from langchain_ollama import ChatOllama


def get_api_key():
    # Deprecated - keeping for compatibility but not used with Ollama
    return None

def require_api_key(func):
    # Deprecated - keeping for compatibility but not enforced with Ollama
    def wrapper(*args, **kwargs):
        return func(None, *args, **kwargs)
    return wrapper

def require_llm(func):
    def wrapper(*args, **kwargs):
        # Using local Ollama model - no API key required
        model_id = "cogito:32b"
        llm = ChatOllama(
            model=model_id,
            temperature=1e-7
        )
        
        return func(llm, *args, **kwargs)
    return wrapper