import sqlite3
import os
import sys

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

def api_key_exists() -> bool:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='api_keys';")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("SELECT id FROM api_keys WHERE id = 1;")
        key_exists = cursor.fetchone()
        return key_exists
        
    return False

def set_api_key(window) -> None:
    api_key = get_valid_api_key(window)
    api_key = api_key.strip()  # Remove leading/trailing whitespace 

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE api_keys (
        id INTEGER PRIMARY KEY,
        key TEXT
    )
    ''')


    cursor.execute('''
    INSERT INTO api_keys (key) VALUES (?)
    ''', (api_key,))

    conn.commit()
    conn.close()

    print(f"API key has been stored in {DB_PATH}.")

def get_valid_api_key(window):
    while True:
        api_key = window.evaluate_js('prompt("Please enter your nVidia nim-API key (must start with nvapi-):")')
        if api_key:
            api_key = api_key.strip()  # Strip leading/trailing spaces
            print(f"Retrieved api_key: '{api_key}'")  # Debugging
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
        return result[0]
    else:
        raise ValueError("API key not found in the database.")