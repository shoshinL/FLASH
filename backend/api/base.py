"""
Base API class providing common functionality for all API modules.
"""

from settings.settings_context import SettingsContext


class BaseAPI:
    """Base class for all API modules with common utilities."""

    @property
    def settings_manager(self):
        """Get the settings manager instance."""
        return SettingsContext.get_settings_manager()
