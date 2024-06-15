import sqlite3
import os
import sys
from cryptography.fernet import Fernet 

ENCRYPTION_KEY = b'FOFbM9Z0p86bFW1KiDwLdvZS7iBr6_1BG5GLkhKlMcc='
fernet = Fernet(ENCRYPTION_KEY)

def get_db_path():
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

DB_PATH = get_db_path()

def api_table_exists() -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys';")
    table_exists = cursor.fetchone()

    conn.close()
    return table_exists

def api_key_exists() -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM api_keys WHERE id = 1;")
    key_exists = cursor.fetchone()

    conn.close()
    return key_exists

def api_key_available() -> bool:
    return api_table_exists() and api_key_exists()

def set_api_key(window) -> None:
    api_key = request_valid_api_key(window)
    api_key = api_key.strip()  # Remove leading/trailing whitespace 

    encrypted_key = fernet.encrypt(api_key.encode())

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not api_table_exists():
        cursor.execute('''
        CREATE TABLE api_keys (
            id INTEGER PRIMARY KEY,
            encrypted_key BLOB
        )
        ''')

    if not api_key_exists():
        cursor.execute('''
        INSERT INTO api_keys (encrypted_key) VALUES (?)
        ''', (encrypted_key,))
    else:
        cursor.execute('''
        UPDATE api_keys SET encrypted_key = ? WHERE id = 1
        ''', (encrypted_key,))

    conn.commit()
    conn.close()

    print(f"Encrypted API key has been stored in {DB_PATH}.")

def request_valid_api_key(window):
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

def get_api_key() -> str:
    conn = sqlite3.connect(DB_PATH)
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
