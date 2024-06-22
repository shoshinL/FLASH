import sqlite3
import os
import sys
from typing import Dict, List, Any
from cryptography.fernet import Fernet 
from ankiUtils.collection_manager import AnkiCollectionManager
from ankiUtils.db_access import get_profiles, get_sync_auth
from anki.errors import DBError

ENCRYPTION_KEY = b'FOFbM9Z0p86bFW1KiDwLdvZS7iBr6_1BG5GLkhKlMcc='
fernet = Fernet(ENCRYPTION_KEY)

class SettingsManager:
    db_path: str
    anki_db_path: str
    profile: str
    deck_name: str
    collection_manager: AnkiCollectionManager
    api_key: str
    decks: Dict[str, int]
    profiles: List[str]

    def __init__(self):
        self.db_path = self._get_db_path()
        if not self._tables_exist():
            self._create_tables()

        if not self._anki_db_path_exists():
            try:
                default_anki_db_path = self._try_get_default_anki_db_path()
                self._upsert_anki_db_path(default_anki_db_path)
                self.anki_db_path = default_anki_db_path
            except FileNotFoundError:
                self.anki_db_path = ""
        else:
            self.anki_db_path = self._get_anki_db_path()

        if self.anki_db_path and not self._profile_exists():
            profiles = self.get_profiles(self.anki_db_path)
            if profiles:
                self._upsert_profile(profiles[0])
                self.profiles = profiles
                self.profile = profiles[0]
            else:
                self.profile = "No profiles found"
        else:
            self.profiles = self.get_profiles(self.anki_db_path)
            self.profile = self._get_profile()

        if self.anki_db_path and self.profile:
            sync_auth = get_sync_auth(self.anki_db_path, self.profile)
            profile_path = os.path.join(os.path.dirname(self.anki_db_path), self.profile)
            self.collection_manager = AnkiCollectionManager(profile_path, sync_auth)
            self.decks = self.collection_manager.get_decks()
            if not self._deck_name_exists():
                if self.decks:
                    deck_name = list(self.decks.keys())[0]
                    self._upsert_deck_name(deck_name)
                    self.deck_name = deck_name
                else:
                    self.deck_name = "No decks found"
            else:
                self.deck_name = self._get_deck_name()
        else:
            self.decks = {}
            self.deck_name = "No decks found"

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

    def _tables_exist(self) -> bool:
        return self._key_table_exists() and self._settings_table_exists()

    def _create_tables(self) -> None:
        if not self._key_table_exists():
            self._create_key_table()
        if not self._settings_table_exists():
            self._create_settings_table()

    def _create_settings_table(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)''')
        conn.commit()
        conn.close()

    def _create_key_table(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS api_keys (id INTEGER PRIMARY KEY, encrypted_key BLOB)''')
        conn.commit()
        conn.close()

    def _key_table_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys';")
        table_exists = cursor.fetchone()
        conn.close()
        return table_exists is not None

    def _settings_table_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings';")
        table_exists = cursor.fetchone()
        conn.close()
        return table_exists is not None

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

    def get_decks(self, profile: str) -> Dict[str, int]:
        if not self.anki_db_path or not profile:
            return {}
        profile_path = os.path.join(os.path.dirname(self.anki_db_path), profile)
        sync_auth = get_sync_auth(self.anki_db_path, profile)
        try:
            collection_manager = self.collection_manager
            return collection_manager.get_decks()
        except DBError as e:
            print(f"DBError occurred: {str(e)}")
            return {"Anki collection already open": -1}
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            return {"Error accessing Anki collection": -1}

    def _upsert_anki_db_path(self, path: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO settings (key, value) VALUES ('anki_db_path', ?)
        ''', (path,))
        conn.commit()
        conn.close()

        self.anki_db_path = path
        
        profiles = self.get_profiles(path)
        if profiles:
            self._upsert_profile(profiles[0])
            self.profile = profiles[0]
        else:
            self.profile = "No profiles found"
        
        decks = self.get_decks(self.profile)
        if decks:
            first_deck_name = list(decks.keys())[0]
            self._upsert_deck_name(first_deck_name)
            self.deck_name = first_deck_name
        else:
            self.deck_name = "No decks found"
        
        return {
            "anki_db_path": path,
            "profiles": profiles,
            "profile": self.profile,
            "decks": decks,
            "deck_name": self.deck_name
        }

    def _upsert_profile(self, profile: str) -> Dict[str, Any]:
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
            self._upsert_deck_name(first_deck_name)
            self.deck_name = first_deck_name
        else:
            self.deck_name = "No decks found"
        
        return {
            "profile": profile,
            "decks": decks,
            "deck_name": self.deck_name
        }

    def _upsert_deck_name(self, deck_name: str) -> None:
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

    def get_settings(self) -> Dict[str, Any]:
        return {
            "anki_db_path": self.anki_db_path,
            "profile": self.profile,
            "deck_name": self.deck_name,
            "api_key_set": self.api_key_exists()
        }

    def api_key_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM api_keys WHERE id = 1;")
        key_exists = cursor.fetchone()
        conn.close()
        return key_exists is not None

    def reset_api_key(self, window) -> None:
        api_key = self._request_valid_api_key(window)
        self._upsert_api_key(api_key)

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

    def _get_api_key(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT encrypted_key FROM api_keys WHERE id = 1')
        result = cursor.fetchone()
        conn.close()
        if result:
            encrypted_key = result[0]
            decrypted_key = fernet.decrypt(encrypted_key).decode()
            return decrypted_key
        else:
            raise ValueError("API key not found in the database.")

    def _request_valid_api_key(self, window) -> str:
        while True:
            api_key = window.evaluate_js('prompt("Please enter your nVidia nim-API key (must start with nvapi-):")')
            if api_key:
                api_key = api_key.strip()
                if api_key.startswith("nvapi-"):
                    return api_key
                else:
                    window.evaluate_js('alert("Invalid API key. The key must start with \'nvapi-\'. Please try again.")')
            else:
                window.evaluate_js('alert("No API key entered. Please try again.")')