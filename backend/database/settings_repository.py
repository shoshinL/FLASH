"""
Settings Repository - Handles all database operations for application settings

This module provides a clean data access layer for settings, API keys, and
provider configurations, separating database concerns from business logic.
"""

import logging
import sqlite3
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SettingsRepository:
    """
    Repository pattern for settings database operations.

    Handles all SQL operations, table creation, and data persistence
    for application settings.
    """

    def __init__(self, db_path: str):
        """
        Initialize repository with database path.

        Args:
            db_path: Absolute path to SQLite database file
        """
        self.db_path = db_path
        self._ensure_tables_exist()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(self.db_path)

    def _ensure_tables_exist(self) -> None:
        """Ensure all required tables exist, create if missing."""
        if not self._tables_exist():
            self._create_tables()

    # ========== Table Management ==========

    def _tables_exist(self) -> bool:
        """Check if all required tables exist."""
        return (
            self._settings_table_exists() and
            self._key_table_exists() and
            self._api_keys_table_exists() and
            self._provider_api_keys_table_exists()
        )

    def _create_tables(self) -> None:
        """Create all required database tables."""
        self._create_settings_table()
        self._create_key_table()
        self._create_api_keys_table()
        self._create_provider_api_keys_table()
        logger.info("Database tables created successfully")

    def _create_settings_table(self) -> None:
        """Create settings table for key-value configuration storage."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

    def _create_key_table(self) -> None:
        """Create key table for legacy API key storage (deprecated)."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS key (
                    key TEXT PRIMARY KEY
                )
            """)

    def _create_api_keys_table(self) -> None:
        """Create api_keys table for legacy encrypted API key storage."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY,
                    encrypted_key BLOB
                )
            """)

    def _create_provider_api_keys_table(self) -> None:
        """Create provider_api_keys table for multi-provider API key storage."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS provider_api_keys (
                    provider TEXT PRIMARY KEY,
                    encrypted_key BLOB
                )
            """)

    def _key_table_exists(self) -> bool:
        """Check if key table exists."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='key'
            """)
            return cursor.fetchone() is not None

    def _api_keys_table_exists(self) -> bool:
        """Check if api_keys table exists."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='api_keys'
            """)
            return cursor.fetchone() is not None

    def _settings_table_exists(self) -> bool:
        """Check if settings table exists."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='settings'
            """)
            return cursor.fetchone() is not None

    def _provider_api_keys_table_exists(self) -> bool:
        """Check if provider_api_keys table exists."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='provider_api_keys'
            """)
            return cursor.fetchone() is not None

    # ========== Settings Operations ==========

    def get_setting(self, key: str) -> Optional[str]:
        """
        Get a setting value by key.

        Args:
            key: Setting key

        Returns:
            Setting value or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM settings WHERE key = ?",
                (key,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def upsert_setting(self, key: str, value: str) -> None:
        """
        Insert or update a setting.

        Args:
            key: Setting key
            value: Setting value
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
            conn.commit()
        logger.debug(f"Upserted setting: {key}")

    def delete_setting(self, key: str) -> None:
        """
        Delete a setting by key.

        Args:
            key: Setting key to delete
        """
        with self._get_connection() as conn:
            conn.execute("DELETE FROM settings WHERE key = ?", (key,))
            conn.commit()
        logger.debug(f"Deleted setting: {key}")

    # ========== Legacy API Key Operations (Deprecated) ==========

    def get_legacy_api_key(self) -> Optional[str]:
        """Get legacy API key (deprecated - use provider-specific keys)."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT key FROM key")
            result = cursor.fetchone()
            return result[0] if result else None

    def upsert_legacy_api_key(self, api_key: str) -> None:
        """Save legacy API key (deprecated - use provider-specific keys)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM key")
            conn.execute("INSERT INTO key (key) VALUES (?)", (api_key,))
            conn.commit()
        logger.debug("Upserted legacy API key")

    # ========== Provider API Keys Operations ==========

    def get_provider_api_key(self, provider: str) -> Optional[bytes]:
        """
        Get encrypted API key for a provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            Encrypted API key (bytes) or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT encrypted_key FROM provider_api_keys WHERE provider = ?",
                (provider,)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def upsert_provider_api_key(self, provider: str, encrypted_api_key: bytes) -> None:
        """
        Save encrypted API key for a provider.

        Args:
            provider: Provider name
            encrypted_api_key: Encrypted API key (bytes)
        """
        with self._get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO provider_api_keys (provider, encrypted_key) VALUES (?, ?)",
                (provider, encrypted_api_key)
            )
            conn.commit()
        logger.debug(f"Upserted API key for provider: {provider}")

    def delete_provider_api_key(self, provider: str) -> None:
        """
        Delete API key for a provider.

        Args:
            provider: Provider name
        """
        with self._get_connection() as conn:
            conn.execute(
                "DELETE FROM provider_api_keys WHERE provider = ?",
                (provider,)
            )
            conn.commit()
        logger.info(f"Deleted API key for provider: {provider}")

    def get_all_provider_api_keys(self) -> Dict[str, bytes]:
        """
        Get all encrypted provider API keys.

        Returns:
            Dictionary mapping provider names to encrypted API keys (bytes)
        """
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT provider, encrypted_key FROM provider_api_keys")
            return {row[0]: row[1] for row in cursor.fetchall()}
