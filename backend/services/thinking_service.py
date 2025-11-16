"""
Thinking service - handles extended thinking/reasoning configuration
"""

import logging
from typing import Dict
from settingUtils.settings_context import SettingsContext

logger = logging.getLogger(__name__)


class ThinkingService:
    """Service for managing thinking/reasoning configuration"""

    # Models that support extended thinking
    THINKING_MODELS = {
        'anthropic': ['claude-3-5-sonnet', 'claude-3-opus', 'claude-3-sonnet'],
        'openai': ['o1', 'o1-mini', 'o1-preview', 'o3-mini'],
        'ollama': ['cogito', 'deepseek-r1', 'qwq'],
        'google': ['gemini-2.0-flash-thinking-exp']
    }

    @staticmethod
    def check_thinking_support(provider: str, model: str) -> Dict:
        """Check if provider/model supports extended thinking"""
        try:
            if not model:
                return {"supports_thinking": False}

            supported_models = ThinkingService.THINKING_MODELS.get(provider, [])
            supports = any(supported_model in model for supported_model in supported_models)

            return {"supports_thinking": supports}
        except Exception as e:
            logger.error(f"Error checking thinking support: {e}")
            return {"supports_thinking": False, "error": str(e)}

    @staticmethod
    def get_thinking_config() -> Dict:
        """Get thinking configuration"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            config = settings_manager.get_thinking_config()
            return config
        except Exception as e:
            logger.error(f"Error getting thinking config: {e}")
            return {
                "enabled": False,
                "budget_tokens": 2000,
                "effort": "medium",
                "summary": "auto",
                "error": str(e)
            }

    @staticmethod
    def set_thinking_config(config: Dict) -> Dict:
        """Set thinking configuration"""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_thinking_config(config)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting thinking config: {e}")
            return {"success": False, "error": str(e)}
