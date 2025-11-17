"""
Provider Configuration Service - Handles LLM provider management.
Uses repository pattern for database operations.
"""

import logging
from typing import Dict, Any, Optional

from security.crypto_manager import CryptoManager


class ProviderConfigService:
    """Service for managing LLM provider configurations and API keys."""

    def __init__(self, repository, crypto_manager: CryptoManager):
        """
        Initialize ProviderConfigService.

        Args:
            repository: SettingsRepository instance for database operations
            crypto_manager: CryptoManager instance for encryption/decryption
        """
        self.repository = repository
        self.crypto_manager = crypto_manager
        self._provider_api_keys = {}  # Cache for provider API keys
        self._load_provider_api_keys()

    def _load_provider_api_keys(self) -> None:
        """Load all provider API keys from database into memory."""
        logging.debug("Loading provider API keys")
        all_keys = self.repository.get_all_provider_api_keys()

        self._provider_api_keys = {}
        for provider, encrypted_key in all_keys.items():
            try:
                decrypted_key = self.crypto_manager.decrypt(encrypted_key).decode()
                self._provider_api_keys[provider] = decrypted_key
            except Exception as e:
                logging.error(f"Failed to decrypt API key for {provider}: {e}")

        logging.debug(f"Loaded API keys for providers: {list(self._provider_api_keys.keys())}")

    def set_provider_api_key(self, provider: str, api_key: str) -> None:
        """
        Set API key for a specific provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic', 'ollama')
            api_key: API key to store
        """
        encrypted_key = self.crypto_manager.encrypt(api_key.strip().encode())
        self.repository.upsert_provider_api_key(provider, encrypted_key)

        # Update cache
        self._provider_api_keys[provider] = api_key.strip()
        logging.debug(f"API key set for provider: {provider}")

    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """
        Get API key for a specific provider.

        Args:
            provider: Provider name

        Returns:
            API key if exists, None otherwise
        """
        return self._provider_api_keys.get(provider)

    def delete_provider_api_key(self, provider: str) -> None:
        """
        Delete API key for a specific provider.

        Args:
            provider: Provider name
        """
        self.repository.delete_provider_api_key(provider)

        # Update cache
        if provider in self._provider_api_keys:
            del self._provider_api_keys[provider]
        logging.debug(f"API key deleted for provider: {provider}")

    def get_all_provider_api_keys(self) -> Dict[str, str]:
        """
        Get all provider API keys (masked for UI display).

        Returns:
            Dictionary of provider names to masked API keys
        """
        return {provider: "***" + key[-4:] if len(key) > 4 else "***"
                for provider, key in self._provider_api_keys.items()}

    def set_provider_config(self, provider: str, model: Optional[str] = None) -> None:
        """
        Set the current provider and model.

        Args:
            provider: Provider name
            model: Model name (optional)
        """
        self.repository.upsert_setting('current_provider', provider)

        if model:
            self.repository.upsert_setting('current_model', model)

        logging.debug(f"Provider config set: {provider}, model: {model}")

    def get_provider_config(self) -> Dict[str, Any]:
        """
        Get the current provider configuration.

        Returns:
            Dictionary with provider, model, and api_key
        """
        # Get current provider
        provider = self.repository.get_setting('current_provider')
        if not provider:
            provider = 'openai'  # Default to OpenAI

        # Get current model
        model = self.repository.get_setting('current_model')

        # Get API key for the current provider
        api_key = self.get_provider_api_key(provider)

        return {
            'provider': provider,
            'model': model,
            'api_key': api_key
        }

    def validate_provider(self, provider: str, api_key: Optional[str] = None,
                         model: Optional[str] = None) -> bool:
        """
        Validate a provider configuration by making a test call.

        Args:
            provider: Provider name
            api_key: API key to test (optional, uses stored key if not provided)
            model: Model to test (optional)

        Returns:
            True if validation succeeds, False otherwise
        """
        try:
            from settings.llm_provider import ProviderFactory

            if provider == 'ollama':
                # Ollama doesn't need API key
                provider_instance = ProviderFactory.get_provider(provider, model=model)
            else:
                if not api_key:
                    return False
                provider_instance = ProviderFactory.get_provider(
                    provider,
                    api_key=api_key,
                    model=model
                )

            return provider_instance.validate_api_key()

        except Exception as e:
            logging.error(f"Provider validation failed: {e}")
            return False

    def has_api_key(self, provider: str) -> bool:
        """
        Check if a provider has an API key stored.

        Args:
            provider: Provider name

        Returns:
            True if API key exists, False otherwise
        """
        return provider in self._provider_api_keys
