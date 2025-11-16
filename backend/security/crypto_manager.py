"""
Crypto Manager - Handles encryption key generation and API key encryption

This module provides secure storage and encryption/decryption of API keys
using Fernet symmetric encryption.
"""

import os
import sys
import logging
from cryptography.fernet import Fernet
from typing import Optional

logger = logging.getLogger(__name__)


class CryptoManager:
    """
    Manages encryption keys and provides encryption/decryption services.

    Uses Fernet symmetric encryption to securely encrypt and decrypt API keys.
    The encryption key is generated once and stored securely in the user's
    data directory.
    """

    def __init__(self):
        """Initialize crypto manager with encryption key."""
        self._encryption_key = self._get_or_create_encryption_key()
        self._fernet = Fernet(self._encryption_key)

    def _get_or_create_encryption_key(self) -> bytes:
        """
        Get or create encryption key for secure storage of API keys.

        The key is generated once on first run and stored in the user's
        data directory with appropriate permissions. On subsequent runs,
        the existing key is loaded.

        Returns:
            Encryption key bytes

        Raises:
            OSError: If unable to create data directory or key file
        """
        # Platform-specific data directory
        if sys.platform == "win32":
            data_dir = os.path.join(os.getenv('APPDATA', ''), 'Flash-for-Anki')
        elif sys.platform == "darwin":
            data_dir = os.path.join(
                os.path.expanduser('~/Library/Application Support/Flash-for-Anki')
            )
        else:  # Linux and other Unix-like systems
            data_dir = os.path.join(
                os.path.expanduser('~/.local/share/Flash-for-Anki')
            )

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
        key_file = os.path.join(data_dir, '.encryption_key')

        # Load existing key or generate new one
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
            logger.debug("Loaded existing encryption key")
        else:
            # Generate new encryption key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)

            # Set restrictive permissions on Unix-like systems
            if sys.platform != "win32":
                os.chmod(key_file, 0o600)

            logger.info("Generated new encryption key")

        return key

    def encrypt(self, plaintext: str) -> bytes:
        """
        Encrypt a plaintext string.

        Args:
            plaintext: String to encrypt (e.g., API key)

        Returns:
            Encrypted bytes

        Raises:
            cryptography.fernet.InvalidToken: If encryption fails
        """
        try:
            encrypted = self._fernet.encrypt(plaintext.encode('utf-8'))
            logger.debug("Successfully encrypted data")
            return encrypted
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, encrypted: bytes) -> str:
        """
        Decrypt encrypted bytes to plaintext string.

        Args:
            encrypted: Encrypted bytes

        Returns:
            Decrypted plaintext string

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
                (wrong key or corrupted data)
        """
        try:
            decrypted = self._fernet.decrypt(encrypted).decode('utf-8')
            logger.debug("Successfully decrypted data")
            return decrypted
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_api_key(self, api_key: str) -> bytes:
        """
        Encrypt an API key for secure storage.

        Convenience method that wraps encrypt() with clearer naming
        for API key use case.

        Args:
            api_key: Plaintext API key

        Returns:
            Encrypted API key bytes
        """
        return self.encrypt(api_key)

    def decrypt_api_key(self, encrypted_key: bytes) -> str:
        """
        Decrypt an API key from storage.

        Convenience method that wraps decrypt() with clearer naming
        for API key use case.

        Args:
            encrypted_key: Encrypted API key bytes

        Returns:
            Decrypted API key string
        """
        return self.decrypt(encrypted_key)


# Singleton instance for global access
_crypto_manager: Optional[CryptoManager] = None


def get_crypto_manager() -> CryptoManager:
    """
    Get singleton CryptoManager instance.

    Returns:
        Global CryptoManager instance
    """
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager
