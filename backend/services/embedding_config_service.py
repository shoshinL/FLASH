"""
Embedding Configuration Service - Handles embedding model configuration.
Uses repository pattern for database operations.
"""

import logging
from typing import Dict, Any, Optional


class EmbeddingConfigService:
    """Service for managing embedding provider configurations."""

    def __init__(self, repository, provider_config_service):
        """
        Initialize EmbeddingConfigService.

        Args:
            repository: SettingsRepository instance for database operations
            provider_config_service: ProviderConfigService instance for API key access
        """
        self.repository = repository
        self.provider_config_service = provider_config_service

    def set_embedding_config(self, provider: str, model: Optional[str] = None) -> None:
        """
        Set the embedding provider and model.

        Args:
            provider: Provider name (e.g., 'openai', 'ollama')
            model: Model name (optional)
        """
        self.repository.upsert_setting('embedding_provider', provider)

        if model:
            self.repository.upsert_setting('embedding_model', model)

        logging.debug(f"Embedding config set: {provider}, model: {model}")

    def get_embedding_config(self) -> Dict[str, Any]:
        """
        Get the current embedding configuration.

        Returns:
            Dictionary with provider, model, and api_key
        """
        # Get embedding provider
        provider = self.repository.get_setting('embedding_provider')
        if not provider:
            provider = 'openai'  # Default to OpenAI

        # Get embedding model
        model = self.repository.get_setting('embedding_model')

        # Get API key for the embedding provider from provider config service
        api_key = self.provider_config_service.get_provider_api_key(provider)

        return {
            'provider': provider,
            'model': model,
            'api_key': api_key
        }

    def get_embedding_provider_with_config(self):
        """
        Get a fully configured embedding provider instance.

        Returns:
            Provider instance configured for embeddings

        Raises:
            ValueError: If API key is required but not found
        """
        from settings.llm_provider import ProviderFactory

        config = self.get_embedding_config()
        provider_name = config['provider']
        model = config['model']
        api_key = config['api_key']

        if provider_name == 'ollama':
            return ProviderFactory.get_provider(provider_name, embedding_model=model)
        else:
            if not api_key:
                raise ValueError(f"API key required for {provider_name}")
            return ProviderFactory.get_provider(
                provider_name,
                api_key=api_key,
                embedding_model=model
            )
