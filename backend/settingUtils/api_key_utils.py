from .settings_context import SettingsContext
from langchain_nvidia_ai_endpoints import ChatNVIDIA


def get_api_key():
    settings_manager = SettingsContext.get_settings_manager()
    return settings_manager.get_api_key()

def require_api_key(func):
    def wrapper(*args, **kwargs):
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key is missing.")
        return func(api_key, *args, **kwargs)
    return wrapper

def require_llm(func):
    def wrapper(*args, **kwargs):
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key is missing.")
        model_id = "meta/llama3-70b-instruct"
        llm = ChatNVIDIA(model=model_id, nvidia_api_key=api_key, temperature=0)
        return func(llm, *args, **kwargs)
    return wrapper