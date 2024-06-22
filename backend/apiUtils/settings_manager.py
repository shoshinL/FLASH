import sqlite3
import os
import sys
from typing import Dict, List
from cryptography.fernet import Fernet 
from ankiUtils.collection_manager import AnkiCollectionManager

from ankiUtils.db_access import get_profiles, get_sync_auth

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

    #TODO: Bind a "guide" modal to the loaded event (as this suggests this is first load)

    def __init__(self):
        self.db_path = self._get_db_path()
        if not self._tables_exist():
            self._create_tables()

        #TODO put the logic into their own methods
        if not self._anki_db_path_exists():
            try:
                default_anki_db_path = self._try_get_default_anki_db_path()
                self._upsert_anki_db_path(default_anki_db_path)
                self.anki_db_path = default_anki_db_path
            except FileNotFoundError:
                self.anki_db_path = "Please select the directory containing your Anki2 database (prefs21.db)"
        else:
            self.anki_db_path = self._get_anki_db_path()

        if self._anki_db_path_exists() and not self._profile_exists():
            profiles = get_profiles(self.anki_db_path)
            if profiles:
                self._upsert_profile(profiles[0])
                self.profiles = profiles
                self.profile = profiles[0]
            else:
                self.profile = "No profiles found"
        else:
            self.profiles = get_profiles(self.anki_db_path)
            self.profile = self._get_profile()

        if self._anki_db_path_exists() and self._profile_exists():
            self.profile = self._get_profile()
            sync_auth = get_sync_auth(self.anki_db_path, self.profile)
            profile_path = os.path.join(os.path.dirname(self.anki_db_path), self.profile)
            self.collection_manager = AnkiCollectionManager(profile_path, sync_auth)
            if not self._deck_name_exists():
                decks = self.collection_manager.get_decks()
                if decks:
                    deck_name = list(decks.keys())[0]
                    self._upsert_deck_name(deck_name)
                    self.decks = decks
                    self.deck_name = deck_name
                else:
                    self.deck_name = "No decks found"
            else:
                self.decks = self.collection_manager.get_decks()
                self.deck_name = self._get_deck_name()
        
        """
        if not self._api_key_exists():
            window.events.loaded += lambda: self._set_api_key_dialog(window)
        else:
            self.api_key = self._get_api_key()        
        """

    def _get_db_path(self):
        # Determine the appropriate application data directory based on the OS
        if sys.platform == 'win32':
            # Windows: Use the APPDATA environment variable
            app_data_dir = os.path.join(os.environ['APPDATA'], 'FLASH for Anki')
        elif sys.platform == 'darwin':
            # macOS: Use the Application Support directory
            app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'FLASH for Anki')
        else:
            # Linux and other Unix-like OSes: Use a dot directory in the user's home directory
            app_data_dir = os.path.join(os.path.expanduser('~'), '.FLASH for Anki')

        # Create the directory if it does not exist
        if not os.path.exists(app_data_dir):
            os.makedirs(app_data_dir)

        # Return the full path to the storage.db file within the application data directory
        return os.path.join(app_data_dir, 'storage.db')

    def _create_settings_table(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT)''')

        conn.commit()
        conn.close()

    def _create_key_table(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''CREATE TABLE api_keys (id INTEGER PRIMARY KEY, encrypted_key BLOB)''')

        conn.commit()
        conn.close()

    def _key_table_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys';")
        table_exists = cursor.fetchone()

        conn.close()
        return table_exists

    def _settings_table_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='settings';")
        table_exists = cursor.fetchone()

        conn.close()
        return table_exists

    def _tables_exist(self) -> bool:
        return self._key_table_exists() and self._settings_table_exists()

    def _create_tables(self) -> None:
        if not self._key_table_exists():
            self._create_key_table(self)
        if not self._settings_table_exists():
            self._create_settings_table(self)

    def _anki_db_path_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = 'anki_db_path';")
        path_exists = cursor.fetchone()

        conn.close()
        return path_exists

    def _upsert_anki_db_path(self, path: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not self.anki_db_path_exists():
            cursor.execute('''
            INSERT INTO settings (key, value) VALUES ('anki_db_path', ?)
            ''', (path,))
        else:
            cursor.execute('''
            UPDATE settings SET value = ? WHERE key = 'anki_db_path'
            ''', (path,))

        conn.commit()
        conn.close()

    def _get_anki_db_path(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = 'anki_db_path';")
        path = cursor.fetchone()

        conn.close()

        if path:
            return path[0]
        else:
            raise ValueError("Anki database path not found in the database.")

    def _profile_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = 'profile';")
        profile_exists = cursor.fetchone()

        conn.close()
        return profile_exists

    def _upsert_profile(self, profile: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not self._profile_exists():
            cursor.execute('''
            INSERT INTO settings (key, value) VALUES ('profile', ?)
            ''', (profile,))
        else:
            cursor.execute('''
            UPDATE settings SET value = ? WHERE key = 'profile'
            ''', (profile,))

        conn.commit()
        conn.close()

    def _get_profile(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = 'profile';")
        profile = cursor.fetchone()

        conn.close()

        if profile:
            return profile[0]
        else:
            raise ValueError("Profile not found in the database.")
        
    def _deck_name_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = 'deck_name';")
        deck_name_exists = cursor.fetchone()

        conn.close()
        return deck_name_exists

    def _upsert_deck_name(self, deck_name: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not self._deck_name_exists():
            cursor.execute('''
                INSERT INTO settings (key, value) VALUES ('deck_name', ?)
            ''', (deck_name,))
        else:
            cursor.execute('''
                UPDATE settings SET value = ? WHERE key = 'deck_name'
            ''', (deck_name,))

        conn.commit()
        conn.close()

    def _get_deck_name(self) -> str:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM settings WHERE key = 'deck_name';")
        deck_name = cursor.fetchone()

        conn.close()

        if deck_name:
            return deck_name[0]
        else:
            raise ValueError("Deck name not found in the database.")

    def _api_key_exists(self) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM api_keys WHERE id = 1;")
        key_exists = cursor.fetchone()

        conn.close()
        return key_exists

    def _upsert_api_key(self, api_key: str) -> None:
        api_key = api_key.strip()  # Remove leading/trailing whitespace 

        encrypted_key = fernet.encrypt(api_key.encode())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not self._api_key_exists():
            cursor.execute('''
            INSERT INTO api_keys (encrypted_key) VALUES (?)
            ''', (encrypted_key,))
        else:
            cursor.execute('''
            UPDATE api_keys SET encrypted_key = ? WHERE id = 1
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

    def _try_get_default_anki_db_path() -> str:
        # Determine the appropriate application data directory based on the OS
        if sys.platform == 'win32':
            # Windows: Use the APPDATA environment variable
            app_data_dir = os.path.join(os.environ['APPDATA'], 'Anki2')
        elif sys.platform == 'darwin':
            # macOS: Use the Application Support directory
            app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'Anki2')
        else:
            # Linux and other Unix-like OSes: Use a dot directory in the user's home directory
            app_data_dir = os.path.join(os.path.expanduser('~/.local/share/'), 'Anki2')

        #Check if the file at os.path.join(app_data_dir, 'prefs21.db') exists
        anki_db_path = os.path.join(app_data_dir, 'prefs21.db')
        if os.path.exists(anki_db_path):
            return anki_db_path
        else:
            raise FileNotFoundError("Anki database path not found.")

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

    def _set_api_key_dialog(self, window):
        api_key = self._request_valid_api_key(window)
        self._upsert_api_key(api_key)

    def reset_api_key(self, window):
        self._set_api_key_dialog(window)