"""
Provider service - handles provider and model operations
"""

import logging
from typing import Dict, List, Optional
from settingUtils.settings_context import SettingsContext
from settingUtils.llm_provider import LLMProviderFactory

logger = logging.getLogger(__name__)


class ProviderService:
    """Service for managing LLM and embedding providers"""

    @staticmethod
    def get_available_providers() -> Dict:
        """Get list of available LLM providers"""
        try:
            providers = LLMProviderFactory.get_available_providers()
            return {"providers": providers, "success": True}
        except Exception as e:
            logger.error(f"Error getting available providers: {e}")
            return {"providers": [], "success": False, "error": str(e)}

    @staticmethod
    def get_available_models(provider: str) -> Dict:
        """Get available models for a provider"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            api_key = settings_manager.get_provider_api_key(provider)

            llm_provider = LLMProviderFactory.create_provider(
                provider_name=provider,
                model_name=None,
                api_key=api_key
            )

            models = llm_provider.get_available_models()
            return {"models": models, "success": True}
        except Exception as e:
            logger.error(f"Error fetching models for {provider}: {e}")
            return {"models": [], "success": False, "error": str(e)}

    @staticmethod
    def get_provider_config() -> Dict:
        """Get current provider configuration"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            config = settings_manager.get_provider_config()
            return {
                "provider": config.get("provider", "openai"),
                "model": config.get("model"),
                "api_key_set": bool(config.get("api_key")),
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting provider config: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def set_provider_config(provider: str, model: Optional[str] = None) -> Dict:
        """Set provider configuration"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_provider_config(provider, model)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting provider config: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_embedding_providers() -> Dict:
        """Get list of available embedding providers"""
        try:
            providers = LLMProviderFactory.get_available_providers()
            return {"providers": providers, "success": True}
        except Exception as e:
            logger.error(f"Error getting embedding providers: {e}")
            return {"providers": [], "success": False, "error": str(e)}

    @staticmethod
    def get_available_embedding_models(provider: str) -> Dict:
        """Get available embedding models for a provider"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            api_key = settings_manager.get_provider_api_key(provider)

            llm_provider = LLMProviderFactory.create_provider(
                provider_name=provider,
                model_name=None,
                api_key=api_key,
                is_embedding=True
            )

            models = llm_provider.get_available_embedding_models()
            return {"models": models, "success": True}
        except Exception as e:
            logger.error(f"Error fetching embedding models for {provider}: {e}")
            return {"models": [], "success": False, "error": str(e)}

    @staticmethod
    def get_embedding_config() -> Dict:
        """Get current embedding configuration"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            config = settings_manager.get_embedding_config()
            return {
                "provider": config.get("provider", "openai"),
                "model": config.get("model"),
                "api_key_set": bool(settings_manager.get_provider_api_key(config.get("provider", "openai"))),
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting embedding config: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def set_embedding_config(provider: str, model: Optional[str] = None) -> Dict:
        """Set embedding configuration"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_embedding_config(provider, model)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting embedding config: {e}")
            return {"success": False, "error": str(e)}
