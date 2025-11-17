"""
Provider Management API

Handles LLM provider configuration, API keys, and model management.
"""

import logging
from .base import BaseAPI

logger = logging.getLogger(__name__)


class ProviderAPI(BaseAPI):
    """API endpoints for LLM provider management."""

    def get_available_providers(self):
        """Get list of all available LLM providers."""
        from settings.llm_provider import ProviderFactory
        providers = ProviderFactory.get_all_providers()
        return {"providers": providers}

    def get_provider_config(self):
        """Get current provider configuration."""
        config = self.settings_manager.get_provider_config()
        # Don't send the actual API key, just whether it's set
        return {
            "provider": config.get("provider", "openai"),
            "model": config.get("model"),
            "api_key_set": config.get("api_key") is not None
        }

    def get_available_models(self, provider):
        """
        Get available models for a specific provider.

        Args:
            provider: Provider name

        Returns:
            Dictionary with models list and status
        """
        from settings.llm_provider import ProviderFactory
        try:
            api_key = self.settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider)
            else:
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key)

            models = provider_instance.get_available_models()
            return {"models": models, "success": True}
        except Exception as e:
            logger.error(f"Error fetching models for {provider}: {e}")
            return {"models": [], "success": False, "error": str(e)}

    def set_provider_api_key(self, provider, api_key):
        """
        Set API key for a specific provider.

        Args:
            provider: Provider name
            api_key: API key to store

        Returns:
            Success status
        """
        try:
            self.settings_manager.set_provider_api_key(provider, api_key)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting API key for {provider}: {e}")
            return {"success": False, "error": str(e)}

    def delete_provider_api_key(self, provider):
        """
        Delete API key for a specific provider.

        Args:
            provider: Provider name

        Returns:
            Success status
        """
        try:
            self.settings_manager.delete_provider_api_key(provider)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting API key for {provider}: {e}")
            return {"success": False, "error": str(e)}

    def get_provider_api_keys_status(self):
        """
        Get status of which providers have API keys set.

        Returns:
            Dictionary with masked API keys
        """
        masked_keys = self.settings_manager.get_all_provider_api_keys()
        return {
            "api_keys": masked_keys,
            "success": True
        }

    def set_provider_config(self, provider, model=None):
        """
        Set current provider and model configuration.

        Args:
            provider: Provider name
            model: Model name (optional)

        Returns:
            Success status
        """
        try:
            self.settings_manager.set_provider_config(provider, model)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting provider config: {e}")
            return {"success": False, "error": str(e)}

    def validate_provider(self, provider, api_key=None, model=None):
        """
        Validate provider configuration with a test call.

        Args:
            provider: Provider name
            api_key: API key to test (optional)
            model: Model to test (optional)

        Returns:
            Validation result
        """
        try:
            is_valid = self.settings_manager.validate_provider(provider, api_key, model)
            return {"valid": is_valid, "success": True}
        except Exception as e:
            logger.error(f"Error validating provider {provider}: {e}")
            return {"valid": False, "success": False, "error": str(e)}

    def set_api_key(self, api_key):
        """
        Legacy method: Set API key for OpenAI.
        Use set_provider_api_key() for new code.

        Args:
            api_key: OpenAI API key

        Returns:
            Success status
        """
        success = self.settings_manager.set_api_key(api_key)
        return {
            "success": success,
            "api_key_set": self.settings_manager.api_key_exists()
        }
