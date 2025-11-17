"""
Anki Integration API

Handles all Anki-related API endpoints including profile and deck management.
"""

import webview
from .base import BaseAPI


class AnkiAPI(BaseAPI):
    """API endpoints for Anki integration."""

    def get_settings(self):
        """Get all application settings including Anki configuration."""
        return self.settings_manager.get_settings()

    def get_profiles(self, anki_db_path):
        """
        Get all available Anki profiles for a database path.

        Args:
            anki_db_path: Path to Anki database

        Returns:
            Dictionary with profiles list
        """
        profiles = self.settings_manager.get_profiles(anki_db_path)
        return {"profiles": profiles}

    def get_decks(self, profile):
        """
        Get all decks for a specific profile.

        Args:
            profile: Profile name

        Returns:
            Dictionary with decks
        """
        decks = self.settings_manager.get_decks(profile)
        return {"decks": decks}

    def get_selected_deck(self):
        """Get the currently selected deck name."""
        return self.settings_manager.deck_name

    def get_selected_profile(self):
        """Get the currently selected profile name."""
        return self.settings_manager.profile

    def select_file_path(self):
        """
        Open file dialog to select Anki database file.

        Returns:
            Dictionary with Anki configuration or error
        """
        file_types = ('Database Files (*.db)',)
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )
        if result and result[0]:
            return self.settings_manager.upsert_anki_db_path(result[0])
        return {"error": "No file selected"}

    def set_profile(self, profile):
        """
        Set the active Anki profile.

        Args:
            profile: Profile name

        Returns:
            Dictionary with configuration
        """
        return self.settings_manager.upsert_profile(profile)

    def set_deck(self, deck_name):
        """
        Set the active deck.

        Args:
            deck_name: Deck name

        Returns:
            Success status
        """
        self.settings_manager.upsert_deck_name(deck_name)
        return {"success": True, "deck_name": deck_name}
