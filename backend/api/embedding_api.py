"""
Embedding Configuration API

Handles embedding provider configuration and model management.
"""

import logging
from .base import BaseAPI

logger = logging.getLogger(__name__)


class EmbeddingAPI(BaseAPI):
    """API endpoints for embedding provider configuration."""

    def get_embedding_providers(self):
        """
        Get list of providers that support embeddings.

        Returns:
            Dictionary with providers list and status
        """
        from settings.llm_provider import ProviderFactory
        try:
            providers = ProviderFactory.get_embedding_providers()
            return {"providers": providers, "success": True}
        except Exception as e:
            logger.error(f"Error getting embedding providers: {e}")
            return {"providers": [], "success": False, "error": str(e)}

    def get_embedding_config(self):
        """
        Get current embedding configuration.

        Returns:
            Dictionary with current embedding provider and model
        """
        try:
            config = self.settings_manager.get_embedding_config()
            # Don't send the actual API key, just whether it's set
            return {
                "provider": config.get("provider", "openai"),
                "model": config.get("model"),
                "api_key_set": config.get("api_key") is not None,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting embedding config: {e}")
            return {"success": False, "error": str(e)}

    def get_available_embedding_models(self, provider):
        """
        Get available embedding models for a specific provider.

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
                if not api_key:
                    return {"models": [], "success": False,
                           "error": "API key required for this provider"}
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key)

            # Check if provider supports embeddings
            if not provider_instance.supports_embeddings():
                return {"models": [], "success": False,
                       "error": f"{provider} does not support embeddings"}

            models = provider_instance.get_available_embedding_models()
            return {"models": models, "success": True}
        except Exception as e:
            logger.error(f"Error fetching embedding models for {provider}: {e}")
            return {"models": [], "success": False, "error": str(e)}

    def set_embedding_config(self, provider, model=None):
        """
        Set the embedding provider and model.

        Args:
            provider: Provider name
            model: Model name (optional)

        Returns:
            Success status
        """
        try:
            from settings.llm_provider import ProviderFactory

            # Validate that provider supports embeddings
            api_key = self.settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider)
            else:
                if not api_key:
                    return {"success": False,
                           "error": f"API key required for {provider}. Please set it first."}
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key)

            if not provider_instance.supports_embeddings():
                return {"success": False,
                       "error": f"{provider} does not support embeddings. Choose OpenAI, Google, or Ollama."}

            # Save configuration
            self.settings_manager.set_embedding_config(provider, model)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting embedding config: {e}")
            return {"success": False, "error": str(e)}
