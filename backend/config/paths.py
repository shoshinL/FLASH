"""
FLASH application path configuration.

Provides centralized path management for application data storage across platforms.
"""

import os
import sys


def get_flash_db_path() -> str:
    """
    Get the path to the FLASH settings database.

    Creates the application data directory if it doesn't exist.

    Returns:
        str: Full path to the storage.db file

    Platform-specific locations:
        - Windows: %APPDATA%/FLASH for Anki/storage.db
        - macOS: ~/Library/Application Support/FLASH for Anki/storage.db
        - Linux: ~/.FLASH for Anki/storage.db
    """
    if sys.platform == 'win32':
        app_data_dir = os.path.join(os.environ['APPDATA'], 'FLASH for Anki')
    elif sys.platform == 'darwin':
        app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'FLASH for Anki')
    else:
        app_data_dir = os.path.join(os.path.expanduser('~'), '.FLASH for Anki')

    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)

    return os.path.join(app_data_dir, 'storage.db')


def get_app_data_dir() -> str:
    """
    Get the application data directory path.

    Creates the directory if it doesn't exist.

    Returns:
        str: Full path to the application data directory
    """
    if sys.platform == 'win32':
        app_data_dir = os.path.join(os.environ['APPDATA'], 'FLASH for Anki')
    elif sys.platform == 'darwin':
        app_data_dir = os.path.join(os.path.expanduser('~/Library/Application Support/'), 'FLASH for Anki')
    else:
        app_data_dir = os.path.join(os.path.expanduser('~'), '.FLASH for Anki')

    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)

    return app_data_dir
