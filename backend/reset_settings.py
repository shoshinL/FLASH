#!/usr/bin/env python3
"""
FLASH Settings Reset Utility

This script helps you reset your FLASH settings database.
Use this when encountering decryption errors or corruption.

Usage:
    python reset_settings.py [options]

Options:
    --full              Delete entire settings database (nuclear option)
    --api-keys          Reset only API keys (recommended for decryption errors)
    --anki              Reset only Anki settings
    --providers         Reset only provider configurations
    --thinking          Reset only thinking configuration
    --backup            Create backup before reset (default)
    --no-backup         Skip backup creation
    --dry-run           Show what would be deleted without actually deleting
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.paths import get_flash_db_path


class SettingsReset:
    """Utility to reset FLASH settings database."""

    def __init__(self):
        self.db_path = get_flash_db_path()
        self.backup_path = None

    def backup_database(self) -> str:
        """
        Create a backup of the settings database.

        Returns:
            Path to backup file
        """
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.dirname(self.db_path)
        backup_filename = f"storage_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)

        shutil.copy2(self.db_path, backup_path)
        print(f"✅ Backup created: {backup_path}")
        self.backup_path = backup_path
        return backup_path

    def reset_full(self, dry_run=False):
        """Delete the entire settings database."""
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            return

        if dry_run:
            print(f"🔍 DRY RUN: Would delete entire database at {self.db_path}")
            return

        os.remove(self.db_path)
        print(f"✅ Deleted entire settings database")
        print(f"   Database will be recreated on next app launch")

    def reset_api_keys(self, dry_run=False):
        """Reset all API keys (fixes decryption errors)."""
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check what would be deleted
        cursor.execute("SELECT COUNT(*) FROM api_keys;")
        api_key_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM provider_api_keys;")
        provider_key_count = cursor.fetchone()[0]

        if dry_run:
            print(f"🔍 DRY RUN: Would delete:")
            print(f"   - {api_key_count} API keys")
            print(f"   - {provider_key_count} provider-specific API keys")
            conn.close()
            return

        # Delete API keys
        cursor.execute("DELETE FROM api_keys;")
        cursor.execute("DELETE FROM provider_api_keys;")

        # Also delete encryption key to force regeneration
        cursor.execute("DELETE FROM settings WHERE key = 'encryption_key';")

        conn.commit()
        conn.close()

        print(f"✅ Reset API keys:")
        print(f"   - Deleted {api_key_count} API keys")
        print(f"   - Deleted {provider_key_count} provider-specific API keys")
        print(f"   - Deleted encryption key (will be regenerated)")
        print(f"\n⚠️  You will need to re-enter all API keys in the app")

    def reset_anki(self, dry_run=False):
        """Reset Anki settings."""
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        anki_keys = ['anki_db_path', 'profile', 'deck_name']

        if dry_run:
            print(f"🔍 DRY RUN: Would delete Anki settings:")
            for key in anki_keys:
                cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
                row = cursor.fetchone()
                if row:
                    print(f"   - {key}: {row[0]}")
            conn.close()
            return

        for key in anki_keys:
            cursor.execute("DELETE FROM settings WHERE key = ?;", (key,))

        conn.commit()
        conn.close()

        print(f"✅ Reset Anki settings:")
        print(f"   - anki_db_path")
        print(f"   - profile")
        print(f"   - deck_name")

    def reset_providers(self, dry_run=False):
        """Reset provider configurations."""
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        provider_keys = ['current_provider', 'current_model', 'embedding_provider', 'embedding_model']

        if dry_run:
            print(f"🔍 DRY RUN: Would delete provider settings:")
            for key in provider_keys:
                cursor.execute("SELECT value FROM settings WHERE key = ?;", (key,))
                row = cursor.fetchone()
                if row:
                    print(f"   - {key}: {row[0]}")
            conn.close()
            return

        for key in provider_keys:
            cursor.execute("DELETE FROM settings WHERE key = ?;", (key,))

        conn.commit()
        conn.close()

        print(f"✅ Reset provider configurations:")
        for key in provider_keys:
            print(f"   - {key}")

    def reset_thinking(self, dry_run=False):
        """Reset thinking configuration."""
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if dry_run:
            cursor.execute("SELECT value FROM settings WHERE key = 'thinking_config';")
            row = cursor.fetchone()
            if row:
                print(f"🔍 DRY RUN: Would delete thinking config: {row[0]}")
            else:
                print(f"🔍 DRY RUN: No thinking config found")
            conn.close()
            return

        cursor.execute("DELETE FROM settings WHERE key = 'thinking_config';")
        conn.commit()
        conn.close()

        print(f"✅ Reset thinking configuration")

    def show_info(self):
        """Show information about the current database."""
        if not os.path.exists(self.db_path):
            print(f"⚠️  No database found at {self.db_path}")
            print(f"   Database will be created on first app launch")
            return

        file_size = os.path.getsize(self.db_path)
        print(f"\n📊 Database Information:")
        print(f"   Location: {self.db_path}")
        print(f"   Size: {file_size:,} bytes")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Count API keys
        cursor.execute("SELECT COUNT(*) FROM api_keys;")
        api_key_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM provider_api_keys;")
        provider_key_count = cursor.fetchone()[0]

        # Get settings
        cursor.execute("SELECT key FROM settings ORDER BY key;")
        settings_keys = [row[0] for row in cursor.fetchall()]

        conn.close()

        print(f"\n   API Keys: {api_key_count}")
        print(f"   Provider API Keys: {provider_key_count}")
        print(f"   Settings: {len(settings_keys)}")
        if settings_keys:
            print(f"      {', '.join(settings_keys)}")

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='FLASH Settings Reset Utility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('--full', action='store_true',
                       help='Delete entire settings database (nuclear option)')
    parser.add_argument('--api-keys', action='store_true',
                       help='Reset only API keys (recommended for decryption errors)')
    parser.add_argument('--anki', action='store_true',
                       help='Reset only Anki settings')
    parser.add_argument('--providers', action='store_true',
                       help='Reset only provider configurations')
    parser.add_argument('--thinking', action='store_true',
                       help='Reset only thinking configuration')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup creation')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    parser.add_argument('--info', action='store_true',
                       help='Show database information and exit')

    args = parser.parse_args()

    resetter = SettingsReset()

    # Show info if requested
    if args.info:
        resetter.show_info()
        return 0

    # If no reset options specified, show help
    if not any([args.full, args.api_keys, args.anki, args.providers, args.thinking]):
        resetter.show_info()
        print("\n" + "="*60)
        print("No reset option specified. Use --help for options.")
        print("\nCommon use cases:")
        print("  Decryption errors:  python reset_settings.py --api-keys")
        print("  Fresh start:        python reset_settings.py --full")
        print("  Check settings:     python reset_settings.py --info")
        print("="*60)
        return 1

    # Show current state
    if not args.dry_run:
        resetter.show_info()
        print("\n" + "="*60)

    # Create backup unless --no-backup or --dry-run
    if not args.no_backup and not args.dry_run:
        resetter.backup_database()

    # Perform resets
    if args.full:
        resetter.reset_full(dry_run=args.dry_run)
    else:
        if args.api_keys:
            resetter.reset_api_keys(dry_run=args.dry_run)
        if args.anki:
            resetter.reset_anki(dry_run=args.dry_run)
        if args.providers:
            resetter.reset_providers(dry_run=args.dry_run)
        if args.thinking:
            resetter.reset_thinking(dry_run=args.dry_run)

    if args.dry_run:
        print("\n" + "="*60)
        print("🔍 DRY RUN COMPLETE - No changes were made")
        print("   Remove --dry-run flag to actually perform the reset")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("✅ Reset complete!")
        if resetter.backup_path:
            print(f"   Backup saved at: {resetter.backup_path}")
        print("="*60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
