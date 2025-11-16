"""
API Key service - handles API key management
"""

import logging
from typing import Dict
from settings.settings_context import SettingsContext

logger = logging.getLogger(__name__)


class APIKeyService:
    """Service for managing API keys"""

    @staticmethod
    def set_api_key(provider: str, api_key: str) -> Dict:
        """Set API key for a provider"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_provider_api_key(provider, api_key)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting API key for {provider}: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def delete_api_key(provider: str) -> Dict:
        """Delete API key for a provider"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.delete_provider_api_key(provider)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting API key for {provider}: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_api_keys_status() -> Dict:
        """Get status of all API keys"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            masked_keys = settings_manager.get_all_provider_api_keys()
            return {
                "api_keys": masked_keys,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting API keys status: {e}")
            return {"api_keys": {}, "success": False, "error": str(e)}
