import sqlite3
import os
import sys
from typing import List
import pickle
from anki.sync import SyncAuth


def get_db_path():
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

    # Return the full path to the storage.db file within the application data directory
    return os.path.join(app_data_dir, 'prefs21.db')

DB_PATH = get_db_path()

def get_profiles() -> List[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM profiles where name != '_global';")

    profiles = cursor.fetchall()
    names = [profile[0] for profile in profiles]
    conn.close()

    return names

def get_sync_auth(profile: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM profiles where name = '{profile}';")
    entry = cursor.fetchone()
    pickled_data = entry[1]
    conn.close()

    data = pickle.loads(pickled_data)
    sync_key = data['syncKey']

    sync_auth = SyncAuth(hkey=sync_key)
    return sync_auth

