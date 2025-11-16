"""
Settings Manager - Coordinator for application settings.
Delegates to specialized services for different concerns.
"""

import sys
import os
import logging
from typing import Dict, List, Any, Optional

from database.settings_repository import SettingsRepository
from security.crypto_manager import get_crypto_manager
from services.anki_service import AnkiService
from services.provider_config_service import ProviderConfigService
from services.embedding_config_service import EmbeddingConfigService
from services.thinking_service import ThinkingService


class SettingsManager:
    """
    Coordinator for application settings.
    Delegates to specialized services for better separation of concerns.
    """

    def __init__(self):
        logging.debug("Initializing SettingsManager")
        self.db_path = self._get_db_path()
        self.repository = SettingsRepository(self.db_path)
        self.crypto_manager = get_crypto_manager()

        # Initialize specialized services
        self.anki_service = AnkiService(self.db_path)
        self.provider_config_service = ProviderConfigService(self.db_path, self.crypto_manager)
        self.embedding_config_service = EmbeddingConfigService(self.db_path, self.provider_config_service)
        self.thinking_service = ThinkingService(self.db_path)

    def _get_db_path(self):
        """Get the path to the FLASH settings database."""
        if sys.platform == 'win32':
            app_data_dir = os.path.join(os.environ['APPDATA'], 'FLASH for Anki')
        elif sys.platform == 'darwin':
            app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'FLASH for Anki')
        else:
            app_data_dir = os.path.join(os.path.expanduser('~'), '.FLASH for Anki')

        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)

        return os.path.join(app_data_dir, 'storage.db')

    def get_settings(self) -> Dict[str, Any]:
        """
        Get all application settings.

        Returns:
            Dictionary containing all settings
        """
        logging.debug("Getting settings")
        anki_config = self.anki_service.get_anki_config()

        # Check if any provider has an API key set
        all_keys = self.provider_config_service.get_all_provider_api_keys()

        return {
            **anki_config,
            "api_key_set": len(all_keys) > 0  # True if any provider has a key
        }

    # ========== Anki Methods (delegate to AnkiService) ==========

    @property
    def anki_db_path(self):
        """Get current Anki database path."""
        return self.anki_service.anki_db_path

    @property
    def profile(self):
        """Get current Anki profile."""
        return self.anki_service.profile

    @property
    def deck_name(self):
        """Get current deck name."""
        return self.anki_service.deck_name

    @property
    def decks(self):
        """Get available decks."""
        return self.anki_service.decks

    @property
    def profiles(self):
        """Get available profiles."""
        return self.anki_service.profiles

    @property
    def collection_manager(self):
        """Get Anki collection manager."""
        return self.anki_service.collection_manager

    def get_profiles(self, anki_db_path: str) -> List[str]:
        """Get all Anki profiles."""
        return self.anki_service.get_profiles(anki_db_path)

    def get_decks(self, profile: str) -> Dict[str, int]:
        """Get all decks for a profile."""
        return self.anki_service.get_decks(profile)

    def upsert_anki_db_path(self, path: str) -> Dict[str, Any]:
        """Set Anki database path."""
        return self.anki_service.upsert_anki_db_path(path)

    def upsert_profile(self, profile: str) -> Dict[str, Any]:
        """Set active Anki profile."""
        return self.anki_service.upsert_profile(profile)

    def upsert_deck_name(self, deck_name: str) -> None:
        """Set active deck."""
        self.anki_service.upsert_deck_name(deck_name)

    def add_generated_cards_to_deck(self, filename: str, notes: List[Dict[str, str]]) -> None:
        """Add generated flashcards to deck."""
        self.anki_service.add_generated_cards_to_deck(filename, notes)

    # ========== Provider Configuration Methods (delegate to ProviderConfigService) ==========

    def set_provider_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a provider."""
        self.provider_config_service.set_provider_api_key(provider, api_key)

    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        return self.provider_config_service.get_provider_api_key(provider)

    def delete_provider_api_key(self, provider: str) -> None:
        """Delete API key for a provider."""
        self.provider_config_service.delete_provider_api_key(provider)

    def get_all_provider_api_keys(self) -> Dict[str, str]:
        """Get all provider API keys (masked)."""
        return self.provider_config_service.get_all_provider_api_keys()

    def set_provider_config(self, provider: str, model: Optional[str] = None) -> None:
        """Set current provider and model."""
        self.provider_config_service.set_provider_config(provider, model)

    def get_provider_config(self) -> Dict[str, Any]:
        """Get current provider configuration."""
        return self.provider_config_service.get_provider_config()

    def validate_provider(self, provider: str, api_key: Optional[str] = None,
                         model: Optional[str] = None) -> bool:
        """Validate provider configuration."""
        return self.provider_config_service.validate_provider(provider, api_key, model)

    # ========== Embedding Configuration Methods (delegate to EmbeddingConfigService) ==========

    def set_embedding_config(self, provider: str, model: Optional[str] = None) -> None:
        """Set embedding provider and model."""
        self.embedding_config_service.set_embedding_config(provider, model)

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration."""
        return self.embedding_config_service.get_embedding_config()

    def get_embedding_provider_with_config(self):
        """Get configured embedding provider instance."""
        return self.embedding_config_service.get_embedding_provider_with_config()

    # ========== Thinking Configuration Methods (delegate to ThinkingService) ==========

    def get_thinking_config(self) -> Dict[str, Any]:
        """Get thinking/reasoning configuration."""
        return self.thinking_service.get_thinking_config()

    def set_thinking_config(self, config: Dict[str, Any]) -> None:
        """Set thinking/reasoning configuration."""
        self.thinking_service.set_thinking_config(config)

    def check_thinking_support(self, provider: str, model: str) -> Dict[str, Any]:
        """Check if a provider/model supports thinking."""
        return self.thinking_service.check_thinking_support(provider, model)

    # ========== Legacy API Key Methods (for backward compatibility) ==========
    # These are kept for compatibility with existing code
    # New code should use provider-specific methods above

    def api_key_exists(self) -> bool:
        """Check if any provider has an API key (legacy method)."""
        all_keys = self.provider_config_service.get_all_provider_api_keys()
        return len(all_keys) > 0

    def get_api_key(self) -> str:
        """Get API key for current provider (legacy method)."""
        config = self.provider_config_service.get_provider_config()
        return config.get('api_key', '')

    def set_api_key(self, api_key: str) -> bool:
        """
        Set API key (legacy method - sets for OpenAI).
        Use set_provider_api_key() instead for new code.
        """
        try:
            # Validate with OpenAI
            from langchain_openai import ChatOpenAI

            model = ChatOpenAI(
                openai_api_key=api_key,
                model="gpt-4o-mini",
                temperature=0.001
            )
            model.invoke("Hello, world!")

            # Store for OpenAI provider
            self.provider_config_service.set_provider_api_key('openai', api_key)
            logging.debug("API key set successfully")
            return True
        except Exception as e:
            logging.error(f"Error setting API key: {e}")
            return False
