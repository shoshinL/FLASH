from functools import wraps
import sqlite3
import os
import sys
import json
from typing import Dict, List, Any, Optional
from cryptography.fernet import Fernet

from anki.collection_manager import AnkiCollectionManager
from anki.db_access import get_profiles, get_sync_auth
from anki.errors import DBError
from database.settings_repository import SettingsRepository
import logging


def _get_or_create_encryption_key() -> bytes:
    """
    Get or create encryption key for secure storage of API keys.

    The key is generated once and stored in the user's data directory.
    This is more secure than hardcoding a key in the source code.

    Returns:
        bytes: The Fernet encryption key
    """
    # Determine the key file location (same directory as database)
    if sys.platform == "win32":
        data_dir = os.path.join(os.getenv('APPDATA'), 'Flash-for-Anki')
    elif sys.platform == "darwin":
        data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/Flash-for-Anki'))
    else:  # Linux and other Unix-like systems
        data_dir = os.path.join(os.path.expanduser('~/.local/share/Flash-for-Anki'))

    # Ensure directory exists
    os.makedirs(data_dir, exist_ok=True)

    key_file = os.path.join(data_dir, '.encryption_key')

    # Load existing key or generate new one
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            key = f.read()
        logging.debug("Loaded existing encryption key")
    else:
        # Generate new key
        key = Fernet.generate_key()
        # Save key to file with restricted permissions
        with open(key_file, 'wb') as f:
            f.write(key)
        # Set file permissions to be readable only by owner (Unix-like systems)
        if sys.platform != "win32":
            os.chmod(key_file, 0o600)
        logging.info("Generated new encryption key")

    return key


# Initialize Fernet with the encryption key
fernet = Fernet(_get_or_create_encryption_key())

class SettingsManager:
    def __init__(self):
        logging.debug("Initializing SettingsManager")
        self.db_path = self._get_db_path()
        self.repository = SettingsRepository(self.db_path)  # Database layer
        self.anki_db_path = ""
        self.profile = ""
        self.deck_name = ""
        self._collection_manager = None
        self.decks = {}
        self.profiles = []
        self._api_key = None
        self._provider_api_keys = {}  # Cache for provider API keys

        self._initialize_anki_settings()
        self._load_api_key()
        self._load_provider_api_keys()

    @property
    def collection_manager(self):
        if self._collection_manager is None:
            self._initialize_collection_manager()
        return self._collection_manager

    def _initialize_anki_settings(self):
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

    def _load_api_key(self):
        logging.debug("Loading API key")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT encrypted_key FROM api_keys WHERE id = 1;")
        encrypted_key = cursor.fetchone()
        conn.close()
        if encrypted_key:
            self._api_key = fernet.decrypt(encrypted_key[0]).decode()
            logging.debug("API key loaded successfully")
        else:
            logging.debug("No API key found in database")



    def _initialize_collection_manager(self):
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

    def get_decks(self, profile):
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

    def get_settings(self):
        logging.debug("Getting settings")
        return {
            "anki_db_path": self.anki_db_path,
            "profile": self.profile,
            "deck_name": self.deck_name,
            "api_key_set": self.api_key_exists(),
            "anki_data_location_valid": self._is_anki_db_path_valid()
        }

    def _get_db_path(self):
        if sys.platform == 'win32':
            app_data_dir = os.path.join(os.environ['APPDATA'], 'FLASH for Anki')
        elif sys.platform == 'darwin':
            app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'FLASH for Anki')
        else:
            app_data_dir = os.path.join(os.path.expanduser('~'), '.FLASH for Anki')

        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)

        return os.path.join(app_data_dir, 'storage.db')

    # Database table management methods removed - now in SettingsRepository

    def _try_get_default_anki_db_path(self) -> str:
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'anki_db_path';")
        path_exists = cursor.fetchone()
        conn.close()
        return path_exists is not None

    def _profile_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'profile';")
        profile_exists = cursor.fetchone()
        conn.close()
        return profile_exists is not None

    def _deck_name_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'deck_name';")
        deck_name_exists = cursor.fetchone()
        conn.close()
        return deck_name_exists is not None

    def get_profiles(self, anki_db_path: str) -> List[str]:
        if not anki_db_path or not os.path.exists(anki_db_path):
            return []
        return get_profiles(anki_db_path)

    def upsert_anki_db_path(self, path: str) -> Dict[str, Any]:
        logging.debug(f"Upserting Anki DB path: {path}")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value) VALUES ('anki_db_path', ?)
        ''', (path,))
        conn.commit()
        conn.close()

        self.anki_db_path = path

        if self._is_anki_db_path_valid():
            profiles = self.get_profiles(path)
            if profiles:
                self.upsert_profile(profiles[0])
                self.profile = profiles[0]
                self._initialize_collection_manager()  # Use our existing method
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value) VALUES ('profile', ?)
        ''', (profile,))
        conn.commit()
        conn.close()

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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value) VALUES ('deck_name', ?)
        ''', (deck_name,))
        conn.commit()
        conn.close()
        self.deck_name = deck_name

    def _get_anki_db_path(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'anki_db_path';")
        path = cursor.fetchone()
        conn.close()
        return path[0] if path else ""

    def _get_profile(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'profile';")
        profile = cursor.fetchone()
        conn.close()
        return profile[0] if profile else ""

    def _get_deck_name(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'deck_name';")
        deck_name = cursor.fetchone()
        conn.close()
        return deck_name[0] if deck_name else ""

    def _is_anki_db_path_valid(self) -> bool:
        return self.anki_db_path and os.path.isfile(self.anki_db_path) and self.anki_db_path.endswith('prefs21.db')

    def api_key_exists(self) -> bool:
        return self._api_key is not None
    
    def set_api_key(self, api_key: str) -> bool:
        # if api_key.startswith("nvapi-"):
        #     try:
        #         model = ChatNVIDIA(model="meta/llama3-70b-instruct", api_key=api_key)
        #         model.invoke("Hello, world!")
        #         self._upsert_api_key(api_key)
        #         self._api_key = api_key  # Update the instance variable
        #         logging.debug("API key set successfully")
        #         return True
        #     except Exception as e:
        #         logging.error(f"Error setting API key: {e}")
        #         return False
        # logging.warning("Invalid API key format")
        # return False

        try:
            # os.
            model_id = "gpt-4.1-nano-2025-04-14"
            # model = init_chat_model(model_id)
            model = ChatOpenAI(
                openai_api_key=api_key,
                model=model_id,
                temperature=0.001
            )

            model.invoke("Hello, world!")
            self._upsert_api_key(api_key)
            self._api_key = api_key  # Update the instance variable
            logging.debug("API key set successfully")
            return True
        except Exception as e:
            logging.error(f"Error setting API key: {e}")
            return False


    def _upsert_api_key(self, api_key: str) -> None:
        api_key = api_key.strip()
        encrypted_key = fernet.encrypt(api_key.encode())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO api_keys (id, encrypted_key) VALUES (1, ?)
        ''', (encrypted_key,))
        conn.commit()
        conn.close()    
        logging.debug("API key upserted in database")
    
    def get_api_key(self) -> str:
        return self._api_key if self._api_key else ""
    
    def add_generated_cards_to_deck(self, filename: str, notes: List[Dict[str, str]]) -> None:
        if not self.collection_manager:
            return
        deck_id = self.decks.get(self.deck_name)
        if deck_id:
            self.collection_manager.add_notes_to_deck(filename, notes, deck_id)
            try:
                self.collection_manager.sync()
            except Exception as e:
                print(f"Error syncing Anki collection: {e}")

    # ========== Provider Configuration Methods ==========

    def _load_provider_api_keys(self) -> None:
        """Load all provider API keys from database into memory."""
        logging.debug("Loading provider API keys")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT provider, encrypted_key FROM provider_api_keys;")
        rows = cursor.fetchall()
        conn.close()

        self._provider_api_keys = {}
        for provider, encrypted_key in rows:
            try:
                decrypted_key = fernet.decrypt(encrypted_key).decode()
                self._provider_api_keys[provider] = decrypted_key
            except Exception as e:
                logging.error(f"Failed to decrypt API key for {provider}: {e}")

        logging.debug(f"Loaded API keys for providers: {list(self._provider_api_keys.keys())}")

    def set_provider_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for a specific provider."""
        encrypted_key = fernet.encrypt(api_key.strip().encode())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO provider_api_keys (provider, encrypted_key)
            VALUES (?, ?)
        ''', (provider, encrypted_key))
        conn.commit()
        conn.close()

        # Update cache
        self._provider_api_keys[provider] = api_key.strip()
        logging.debug(f"API key set for provider: {provider}")

    def get_provider_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        return self._provider_api_keys.get(provider)

    def delete_provider_api_key(self, provider: str) -> None:
        """Delete API key for a specific provider."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM provider_api_keys WHERE provider = ?', (provider,))
        conn.commit()
        conn.close()

        # Update cache
        if provider in self._provider_api_keys:
            del self._provider_api_keys[provider]
        logging.debug(f"API key deleted for provider: {provider}")

    def get_all_provider_api_keys(self) -> Dict[str, str]:
        """Get all provider API keys (for UI display - masked)."""
        return {provider: "***" + key[-4:] if len(key) > 4 else "***"
                for provider, key in self._provider_api_keys.items()}

    def set_provider_config(self, provider: str, model: Optional[str] = None) -> None:
        """Set the current provider and model."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES ('current_provider', ?)
        ''', (provider,))

        if model:
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) VALUES ('current_model', ?)
            ''', (model,))

        conn.commit()
        conn.close()
        logging.debug(f"Provider config set: {provider}, model: {model}")

    def get_provider_config(self) -> Dict[str, Any]:
        """Get the current provider configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get current provider
        cursor.execute("SELECT value FROM settings WHERE key = 'current_provider';")
        provider_row = cursor.fetchone()
        provider = provider_row[0] if provider_row else 'openai'  # Default to OpenAI

        # Get current model
        cursor.execute("SELECT value FROM settings WHERE key = 'current_model';")
        model_row = cursor.fetchone()
        model = model_row[0] if model_row else None

        conn.close()

        # Get API key for the current provider
        api_key = self.get_provider_api_key(provider)

        return {
            'provider': provider,
            'model': model,
            'api_key': api_key
        }

    def validate_provider(self, provider: str, api_key: Optional[str] = None,
                         model: Optional[str] = None) -> bool:
        """Validate a provider configuration by making a test call."""
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

    # ========== Embedding Configuration Methods ==========

    def set_embedding_config(self, provider: str, model: Optional[str] = None) -> None:
        """Set the embedding provider and model."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES ('embedding_provider', ?)
        ''', (provider,))

        if model:
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) VALUES ('embedding_model', ?)
            ''', (model,))

        conn.commit()
        conn.close()
        logging.debug(f"Embedding config set: {provider}, model: {model}")

    def get_embedding_config(self) -> Dict[str, Any]:
        """Get the current embedding configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get embedding provider
        cursor.execute("SELECT value FROM settings WHERE key = 'embedding_provider';")
        provider_row = cursor.fetchone()
        provider = provider_row[0] if provider_row else 'openai'  # Default to OpenAI

        # Get embedding model
        cursor.execute("SELECT value FROM settings WHERE key = 'embedding_model';")
        model_row = cursor.fetchone()
        model = model_row[0] if model_row else None

        conn.close()

        # Get API key for the embedding provider
        api_key = self.get_provider_api_key(provider)

        return {
            'provider': provider,
            'model': model,
            'api_key': api_key
        }

    def get_embedding_provider_with_config(self):
        """Get a fully configured embedding provider instance."""
        from settings.llm_provider import ProviderFactory

        config = self.get_embedding_config()
        provider_name = config['provider']
        model = config['model']
        api_key = config['api_key']

        if provider_name == 'ollama':
            return ProviderFactory.get_provider(provider_name, embedding_model=model)
        else:
            if not api_key:
                raise ValueError(f"API key required for {provider_name}")
            return ProviderFactory.get_provider(
                provider_name,
                api_key=api_key,
                embedding_model=model
            )

    # ========== Thinking/Reasoning Configuration Methods ==========

    def get_thinking_config(self) -> Dict[str, Any]:
        """Get thinking/reasoning configuration."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = 'thinking_config';")
        config_row = cursor.fetchone()
        conn.close()

        if config_row:
            try:
                return json.loads(config_row[0])
            except json.JSONDecodeError:
                logging.error("Failed to parse thinking config JSON")
                return self._default_thinking_config()
        else:
            return self._default_thinking_config()

    def _default_thinking_config(self) -> Dict[str, Any]:
        """Get default thinking configuration."""
        return {
            'enabled': False,
            'budget_tokens': 2000,      # For Claude
            'effort': 'medium',         # For OpenAI (low/medium/high)
            'summary': 'auto'           # Deprecated (kept for backward compatibility, not used)
        }

    def set_thinking_config(self, config: Dict[str, Any]) -> None:
        """Set thinking/reasoning configuration."""
        # Merge with defaults to ensure all fields are present
        full_config = self._default_thinking_config()
        full_config.update(config)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES ('thinking_config', ?)
        ''', (json.dumps(full_config),))
        conn.commit()
        conn.close()
        logging.debug(f"Thinking config set: {full_config}")