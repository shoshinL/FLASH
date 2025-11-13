from .settings_context import SettingsContext
from .llm_provider import ProviderFactory
import logging


def get_api_key():
    """Get API key for the current provider (deprecated - use get_provider_config)."""
    settings_manager = SettingsContext.get_settings_manager()
    return settings_manager.get_api_key()


def get_provider_config():
    """Get the current LLM provider configuration."""
    settings_manager = SettingsContext.get_settings_manager()
    return settings_manager.get_provider_config()


def require_api_key(func):
    """Decorator for functions that require an API key (deprecated - use require_llm)."""
    def wrapper(*args, **kwargs):
        api_key = get_api_key()
        if not api_key:
            raise ValueError("API key is missing.")
        return func(api_key, *args, **kwargs)
    return wrapper


def require_llm(func):
    """Decorator that provides an LLM instance based on the configured provider."""
    def wrapper(*args, **kwargs):
        settings_manager = SettingsContext.get_settings_manager()
        provider_config = settings_manager.get_provider_config()

        provider_name = provider_config.get('provider', 'openai')
        model = provider_config.get('model')
        api_key = provider_config.get('api_key')

        # Create provider instance
        try:
            if provider_name == 'ollama':
                # Ollama doesn't need API key
                provider = ProviderFactory.get_provider(
                    provider_name,
                    model=model
                )
            else:
                # Other providers need API key
                if not api_key:
                    raise ValueError(f"API key is required for {provider_name}")
                provider = ProviderFactory.get_provider(
                    provider_name,
                    api_key=api_key,
                    model=model
                )

            # Get LLM instance
            llm = provider.get_llm()
            logging.debug(f"Using {provider_name} provider with model {model}")

            return func(llm, *args, **kwargs)

        except Exception as e:
            logging.error(f"Failed to initialize LLM provider: {e}")
            raise

    return wrapper