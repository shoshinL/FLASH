"""
Thinking/Reasoning Configuration API

Handles extended thinking configuration for LLM models that support reasoning.
"""

import logging
from .base import BaseAPI

logger = logging.getLogger(__name__)


class ThinkingAPI(BaseAPI):
    """API endpoints for thinking/reasoning configuration."""

    def get_thinking_config(self):
        """
        Get thinking/reasoning configuration.

        Returns:
            Dictionary with thinking configuration (enabled, budget_tokens, effort, summary)
        """
        try:
            config = self.settings_manager.get_thinking_config()
            return config
        except Exception as e:
            logger.error(f"Error getting thinking config: {e}")
            return {
                "enabled": False,
                "budget_tokens": 2000,
                "effort": "medium",
                "summary": "auto"
            }

    def set_thinking_config(self, config):
        """
        Set thinking/reasoning configuration.

        Args:
            config: Configuration dictionary with thinking settings

        Returns:
            Success status
        """
        try:
            self.settings_manager.set_thinking_config(config)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting thinking config: {e}")
            return {"success": False, "error": str(e)}

    def check_thinking_support(self, provider, model):
        """
        Check if a provider/model supports thinking/reasoning.

        Args:
            provider: Provider name
            model: Model name

        Returns:
            Dictionary with supports_thinking boolean and status
        """
        from settings.llm_provider import ProviderFactory
        try:
            api_key = self.settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider, model=model)
            else:
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key, model=model)

            supports_thinking = provider_instance.supports_thinking()
            return {"supports_thinking": supports_thinking, "success": True}
        except Exception as e:
            logger.error(f"Error checking thinking support for {provider}/{model}: {e}")
            return {"supports_thinking": False, "success": False, "error": str(e)}
