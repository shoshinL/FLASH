import sqlite3
from typing import List
import pickle
from anki.sync import SyncAuth

# TODO move these to settings_manager
def get_profiles(anki_db_path: str) -> List[str]:
    conn = sqlite3.connect(anki_db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM profiles where name != '_global';")

    profiles = cursor.fetchall()
    names = [profile[0] for profile in profiles]
    conn.close()

    return names

def get_sync_auth(anki_db_path: str, profile: str) -> SyncAuth:
    conn = sqlite3.connect(anki_db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM profiles where name = '{profile}';")
    entry = cursor.fetchone()
    pickled_data = entry[1]
    conn.close()

    data = pickle.loads(pickled_data)
    sync_key = data['syncKey']

    sync_auth = SyncAuth(hkey=sync_key)
    return sync_auth

