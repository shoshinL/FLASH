from .settings_context import SettingsContext

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