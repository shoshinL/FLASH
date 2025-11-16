"""
Embedding Configuration Service - Handles embedding model configuration.
Extracted from SettingsManager for better separation of concerns.
"""

import sqlite3
import logging
from typing import Dict, Any, Optional


class EmbeddingConfigService:
    """Service for managing embedding provider configurations."""

    def __init__(self, db_path: str, provider_config_service):
        """
        Initialize EmbeddingConfigService.

        Args:
            db_path: Path to the FLASH settings database
            provider_config_service: ProviderConfigService instance for API key access
        """
        self.db_path = db_path
        self.provider_config_service = provider_config_service

    def set_embedding_config(self, provider: str, model: Optional[str] = None) -> None:
        """
        Set the embedding provider and model.

        Args:
            provider: Provider name (e.g., 'openai', 'ollama')
            model: Model name (optional)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES ('embedding_provider', ?)
        ''', (provider,))

        if model:
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) VALUES ('embedding_model', ?)
            ''', (model,))

        conn.commit()
        conn.close()
        logging.debug(f"Embedding config set: {provider}, model: {model}")

    def get_embedding_config(self) -> Dict[str, Any]:
        """
        Get the current embedding configuration.

        Returns:
            Dictionary with provider, model, and api_key
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get embedding provider
        cursor.execute("SELECT value FROM settings WHERE key = 'embedding_provider';")
        provider_row = cursor.fetchone()
        provider = provider_row[0] if provider_row else 'openai'  # Default to OpenAI

        # Get embedding model
        cursor.execute("SELECT value FROM settings WHERE key = 'embedding_model';")
        model_row = cursor.fetchone()
        model = model_row[0] if model_row else None

        conn.close()

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
