"""
Anki Service - Handles all Anki-related operations.
Uses repository pattern for database operations.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

from anki.errors import DBError
from anki_utils.collection_manager import AnkiCollectionManager
from anki_utils.db_access import get_profiles, get_sync_auth


class AnkiService:
    """Service for managing Anki profiles, decks, and collection operations."""

    def __init__(self, repository):
        """
        Initialize AnkiService.

        Args:
            repository: SettingsRepository instance for database operations
        """
        self.repository = repository
        self.anki_db_path = ""
        self.profile = ""
        self.deck_name = ""
        self._collection_manager = None
        self.decks = {}
        self.profiles = []

        self._initialize_anki_settings()

    @property
    def collection_manager(self):
        """Lazy-load collection manager."""
        if self._collection_manager is None:
            self._initialize_collection_manager()
        return self._collection_manager

    def _initialize_anki_settings(self):
        """Initialize Anki settings from database."""
        logging.debug("Initializing Anki settings")
        if not self._anki_db_path_exists():
            try:
                default_anki_db_path = self._try_get_default_anki_db_path()
                self.upsert_anki_db_path(default_anki_db_path)
                self.anki_db_path = default_anki_db_path
            except FileNotFoundError:
                logging.warning("Default Anki DB path not found")
                self.anki_db_path = ""
        else:
            self.anki_db_path = self._get_anki_db_path()

        logging.debug(f"Anki DB path: {self.anki_db_path}")

        if self.anki_db_path:
            self.profiles = self.get_profiles(self.anki_db_path)
            logging.debug(f"Profiles: {self.profiles}")
            if not self._profile_exists() and self.profiles:
                self.upsert_profile(self.profiles[0])
            self.profile = self._get_profile()
            logging.debug(f"Selected profile: {self.profile}")

            if self.profile:
                self.deck_name = self._get_deck_name()
                logging.debug(f"Selected deck: {self.deck_name}")

    def _initialize_collection_manager(self):
        """Initialize the Anki collection manager."""
        logging.debug("Initializing collection manager")
        if not self.anki_db_path or not self.profile:
            logging.warning("Cannot initialize collection manager: Anki DB path or profile not set")
            return

        if self._collection_manager is not None:
            logging.debug("Collection manager already initialized")
            return

        try:
            sync_auth = get_sync_auth(self.anki_db_path, self.profile)
            profile_path = os.path.join(os.path.dirname(self.anki_db_path), self.profile)
            logging.debug(f"Attempting to create AnkiCollectionManager with profile path: {profile_path}")
            self._collection_manager = AnkiCollectionManager(profile_path, sync_auth)
            self.decks = self._collection_manager.get_decks()
            logging.debug(f"Collection manager initialized successfully. Decks: {self.decks}")
        except DBError as e:
            logging.error(f"DBError initializing collection manager: {e}")
            self._collection_manager = None
            raise
        except Exception as e:
            logging.error(f"Unexpected error initializing collection manager: {e}")
            self._collection_manager = None
            raise

    def get_decks(self, profile: str) -> Dict[str, int]:
        """
        Get all decks for a profile.

        Args:
            profile: Profile name

        Returns:
            Dictionary of deck names to deck IDs
        """
        logging.debug(f"Getting decks for profile: {profile}")
        if not self.anki_db_path or not profile:
            logging.warning("Cannot get decks: Anki DB path or profile not set")
            return {}
        try:
            if not self._collection_manager:
                self._initialize_collection_manager()
            self.decks = self._collection_manager.get_decks()
            logging.debug(f"Decks: {self.decks}")
            return self.decks
        except DBError as e:
            logging.error(f"DBError occurred while getting decks: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Unexpected error occurred while getting decks: {str(e)}")
            return {"Error accessing Anki collection": -1}

    def get_profiles(self, anki_db_path: str) -> List[str]:
        """
        Get all Anki profiles.

        Args:
            anki_db_path: Path to Anki prefs21.db

        Returns:
            List of profile names
        """
        if not anki_db_path or not os.path.exists(anki_db_path):
            return []
        return get_profiles(anki_db_path)

    def upsert_anki_db_path(self, path: str) -> Dict[str, Any]:
        """
        Set the Anki database path and initialize profiles/decks.

        Args:
            path: Path to Anki prefs21.db

        Returns:
            Dictionary with Anki configuration
        """
        logging.debug(f"Upserting Anki DB path: {path}")
        self.repository.upsert_setting('anki_db_path', path)

        self.anki_db_path = path

        if self._is_anki_db_path_valid():
            profiles = self.get_profiles(path)
            if profiles:
                self.upsert_profile(profiles[0])
                self.profile = profiles[0]
                self._initialize_collection_manager()
                decks = self.get_decks(self.profile)
                if decks:
                    first_deck_name = list(decks.keys())[0]
                    self.upsert_deck_name(first_deck_name)
                    self.deck_name = first_deck_name
                else:
                    self.deck_name = "No decks found"
            else:
                self.profile = "No profiles found"
                self.deck_name = "No decks found"

            return {
                "anki_db_path": path,
                "profiles": profiles,
                "profile": self.profile,
                "decks": decks,
                "deck_name": self.deck_name
            }
        else:
            self.anki_db_path = ""
            return {
                "anki_db_path": "",
                "profiles": [],
                "profile": "",
                "decks": {},
                "deck_name": ""
            }

    def upsert_profile(self, profile: str) -> Dict[str, Any]:
        """
        Set the active Anki profile.

        Args:
            profile: Profile name

        Returns:
            Dictionary with profile and deck configuration
        """
        self.repository.upsert_setting('profile', profile)

        self.profile = profile

        decks = self.get_decks(profile)
        if decks:
            first_deck_name = list(decks.keys())[0]
            self.upsert_deck_name(first_deck_name)
            self.deck_name = first_deck_name
        else:
            self.deck_name = "No decks found"

        return {
            "profile": profile,
            "decks": decks,
            "deck_name": self.deck_name
        }

    def upsert_deck_name(self, deck_name: str) -> None:
        """
        Set the active deck.

        Args:
            deck_name: Deck name
        """
        self.repository.upsert_setting('deck_name', deck_name)
        self.deck_name = deck_name

    def add_generated_cards_to_deck(self, filename: str, notes: List[Dict[str, str]]) -> None:
        """
        Add generated flashcards to the current deck.

        Args:
            filename: Source filename for the notes
            notes: List of note dictionaries with 'front' and 'back' keys
        """
        if not self.collection_manager:
            return
        deck_id = self.decks.get(self.deck_name)
        if deck_id:
            self.collection_manager.add_notes_to_deck(filename, notes, deck_id)
            try:
                self.collection_manager.sync()
            except Exception as e:
                print(f"Error syncing Anki collection: {e}")

    def get_anki_config(self) -> Dict[str, Any]:
        """
        Get current Anki configuration.

        Returns:
            Dictionary with anki_db_path, profile, deck_name, and validation status
        """
        return {
            "anki_db_path": self.anki_db_path,
            "profile": self.profile,
            "deck_name": self.deck_name,
            "anki_data_location_valid": self._is_anki_db_path_valid()
        }

    # ========== Private Helper Methods ==========

    def _try_get_default_anki_db_path(self) -> str:
        """Try to find the default Anki database path."""
        if sys.platform == 'win32':
            app_data_dir = os.path.join(os.environ['APPDATA'], 'Anki2')
        elif sys.platform == 'darwin':
            app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'Anki2')
        else:
            app_data_dir = os.path.join(os.path.expanduser('~/.local/share/'), 'Anki2')

        anki_db_path = os.path.join(app_data_dir, 'prefs21.db')
        if os.path.exists(anki_db_path):
            return anki_db_path
        else:
            raise FileNotFoundError("Anki database path not found.")

    def _anki_db_path_exists(self) -> bool:
        """Check if anki_db_path is stored in settings."""
        return self.repository.get_setting('anki_db_path') is not None

    def _profile_exists(self) -> bool:
        """Check if profile is stored in settings."""
        return self.repository.get_setting('profile') is not None

    def _deck_name_exists(self) -> bool:
        """Check if deck_name is stored in settings."""
        return self.repository.get_setting('deck_name') is not None

    def _get_anki_db_path(self) -> str:
        """Get anki_db_path from settings."""
        return self.repository.get_setting('anki_db_path') or ""

    def _get_profile(self) -> str:
        """Get profile from settings."""
        return self.repository.get_setting('profile') or ""

    def _get_deck_name(self) -> str:
        """Get deck_name from settings."""
        return self.repository.get_setting('deck_name') or ""

    def _is_anki_db_path_valid(self) -> bool:
        """Validate that anki_db_path exists and is valid."""
        return self.anki_db_path and os.path.isfile(self.anki_db_path) and self.anki_db_path.endswith('prefs21.db')
