"""
Thinking Service - Handles extended thinking/reasoning configuration.
Uses repository pattern for database operations.
"""

import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ThinkingService:
    """Service for managing thinking/reasoning configuration."""

    # Models that support extended thinking
    THINKING_MODELS = {
        'anthropic': ['claude-3-5-sonnet', 'claude-3-opus', 'claude-3-sonnet'],
        'openai': ['o1', 'o1-mini', 'o1-preview', 'o3-mini'],
        'ollama': ['cogito', 'deepseek-r1', 'qwq'],
        'google': ['gemini-2.0-flash-thinking-exp']
    }

    def __init__(self, repository):
        """
        Initialize ThinkingService.

        Args:
            repository: SettingsRepository instance for database operations
        """
        self.repository = repository

    def get_thinking_config(self) -> Dict[str, Any]:
        """
        Get thinking/reasoning configuration from database.

        Returns:
            Dictionary with thinking configuration
        """
        try:
            config_json = self.repository.get_setting('thinking_config')

            if config_json:
                try:
                    return json.loads(config_json)
                except json.JSONDecodeError:
                    logger.error("Failed to parse thinking config JSON")
                    return self._default_thinking_config()
            else:
                return self._default_thinking_config()
        except Exception as e:
            logger.error(f"Error getting thinking config: {e}")
            return self._default_thinking_config()

    def set_thinking_config(self, config: Dict[str, Any]) -> None:
        """
        Set thinking/reasoning configuration in database.

        Args:
            config: Thinking configuration dictionary
        """
        try:
            # Merge with defaults to ensure all fields are present
            full_config = self._default_thinking_config()
            full_config.update(config)

            self.repository.upsert_setting('thinking_config', json.dumps(full_config))
            logger.debug(f"Thinking config set: {full_config}")
        except Exception as e:
            logger.error(f"Error setting thinking config: {e}")
            raise

    def check_thinking_support(self, provider: str, model: str) -> Dict[str, Any]:
        """
        Check if provider/model supports extended thinking.

        Args:
            provider: Provider name (e.g., 'anthropic', 'openai')
            model: Model name

        Returns:
            Dictionary with 'supports_thinking' boolean
        """
        try:
            if not model:
                return {"supports_thinking": False}

            supported_models = self.THINKING_MODELS.get(provider, [])
            supports = any(supported_model in model for supported_model in supported_models)

            return {"supports_thinking": supports}
        except Exception as e:
            logger.error(f"Error checking thinking support: {e}")
            return {"supports_thinking": False, "error": str(e)}

    def _default_thinking_config(self) -> Dict[str, Any]:
        """
        Get default thinking configuration.

        Returns:
            Default thinking configuration dictionary
        """
        return {
            'enabled': False,
            'budget_tokens': 2000,      # For Claude
            'effort': 'medium',         # For OpenAI (low/medium/high)
            'summary': 'auto'           # Deprecated (kept for backward compatibility)
        }
