# Database Schema Documentation

## Overview

FLASH uses SQLite for local settings storage. The database is located at:

- **Linux:** `~/.FLASH for Anki/storage.db`
- **macOS:** `~/Library/Application Support/FLASH for Anki/storage.db`
- **Windows:** `%APPDATA%\FLASH for Anki\storage.db`

---

## Tables

### 1. `settings`

**Purpose:** General key-value configuration storage

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
```

**Common Keys:**
- `anki_db_path` - Path to Anki prefs21.db
- `profile` - Current Anki profile name
- `deck_name` - Current Anki deck name
- `current_provider` - Active LLM provider (e.g., 'openai', 'anthropic')
- `current_model` - Active model name
- `embedding_provider` - Provider for embeddings
- `embedding_model` - Model for embeddings
- `thinking_config` - JSON string with thinking configuration
- `encryption_key` - Base64 encoded encryption key (auto-generated)

**Example:**
```sql
INSERT INTO settings (key, value) VALUES ('current_provider', 'openai');
```

---

### 2. `key`

**Purpose:** Legacy API key storage (deprecated, use `provider_api_keys` instead)

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS key (
    key TEXT PRIMARY KEY
)
```

**Status:** Deprecated - maintained for backward compatibility

---

### 3. `api_keys`

**Purpose:** Legacy encrypted API key storage (deprecated)

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY,
    encrypted_key BLOB
)
```

**Notes:**
- Stores encrypted API keys as BLOB
- Typically only one row with id=1
- Deprecated in favor of provider-specific keys

---

### 4. `provider_api_keys`

**Purpose:** Multi-provider encrypted API key storage

**Schema:**
```sql
CREATE TABLE IF NOT EXISTS provider_api_keys (
    provider TEXT PRIMARY KEY,
    encrypted_key BLOB
)
```

**Supported Providers:**
- `openai`
- `anthropic`
- `google`
- `openrouter`
- `ollama` (no API key needed)

**Example:**
```sql
INSERT INTO provider_api_keys (provider, encrypted_key)
VALUES ('openai', X'...');  -- encrypted blob
```

**Encryption:**
- Keys are encrypted using `cryptography.fernet.Fernet`
- Encryption key stored in `settings` table as `encryption_key`
- Encryption key is auto-generated on first use

---

## Schema Migration History

### Version 1 (Initial)
- `settings` table
- `key` table

### Version 2 (Multi-provider support)
- Added `provider_api_keys` table
- Added `api_keys` table

### Version 3 (Current) - Fixed Column Name
- Fixed `provider_api_keys.encrypted_api_key` → `encrypted_key`
- Ensured all tables created consistently

---

## Common Operations

### Get All Settings
```python
from database.settings_repository import SettingsRepository

repo = SettingsRepository('/path/to/storage.db')
provider = repo.get_setting('current_provider')
```

### Store Encrypted API Key
```python
from security.crypto_manager import get_crypto_manager

crypto = get_crypto_manager()
encrypted = crypto.encrypt(b"sk-your-api-key")
repo.upsert_provider_api_key('openai', encrypted)
```

### Retrieve and Decrypt API Key
```python
encrypted = repo.get_provider_api_key('openai')
if encrypted:
    api_key = crypto.decrypt(encrypted).decode()
```

---

## Database Initialization

Tables are created automatically on first run by `SettingsRepository.__init__()`:

```python
class SettingsRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_tables_exist()  # Creates all tables if missing
```

---

## Reset Settings

Use the provided utility to reset corrupted settings:

```bash
# Fix decryption errors
python reset_settings.py --api-keys

# Delete everything
python reset_settings.py --full

# See what's in the database
python reset_settings.py --info
```

See `HOW_TO_RESET_SETTINGS.md` for details.

---

## Schema Verification

To verify the schema is correct:

```python
import sqlite3

conn = sqlite3.connect('storage.db')
cursor = conn.cursor()

# Check tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
print("Tables:", [row[0] for row in cursor.fetchall()])

# Check provider_api_keys schema
cursor.execute("PRAGMA table_info(provider_api_keys)")
for row in cursor.fetchall():
    print(f"Column: {row[1]}, Type: {row[2]}")

conn.close()
```

Expected output:
```
Tables: ['api_keys', 'key', 'provider_api_keys', 'settings']
Column: provider, Type: TEXT
Column: encrypted_key, Type: BLOB
```

---

## Known Issues & Fixes

### Issue: "no such column: encrypted_key"

**Symptom:**
```
ERROR - Unexpected error occurred: no such column: encrypted_key
```

**Cause:** Database created with old schema before fix

**Solution:**
```bash
# Delete the database (will be recreated with correct schema)
python reset_settings.py --full
```

Or manually:
```bash
rm ~/.FLASH\ for\ Anki/storage.db
```

### Issue: Decryption errors

**Symptom:**
```
ERROR - Failed to decrypt API key for openai
```

**Cause:** Encryption key changed or corrupted

**Solution:**
```bash
python reset_settings.py --api-keys
```

Then re-enter your API keys in the app.

---

## Type Safety

The repository uses proper type hints:

```python
def get_provider_api_key(self, provider: str) -> Optional[bytes]:
    """Returns encrypted key as bytes or None"""

def upsert_provider_api_key(self, provider: str, encrypted_api_key: bytes) -> None:
    """Accepts encrypted key as bytes"""
```

**Important:** Encrypted keys are `bytes`, not `str`!

---

## Testing

To test the database schema:

```bash
cd backend
python3 -c "
from database.settings_repository import SettingsRepository
import tempfile
import os

with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
    db_path = f.name

repo = SettingsRepository(db_path)
print('✅ Database initialized successfully')

# Verify tables
import sqlite3
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\" ORDER BY name')
tables = [row[0] for row in cursor.fetchall()]
print(f'Tables: {tables}')
conn.close()

os.remove(db_path)
"
```

---

## Repository Pattern

The database layer uses the Repository pattern for clean separation:

```
Application Code
    ↓
SettingsManager (Coordinator)
    ↓
Services (Business Logic)
    ↓
SettingsRepository (Data Access)
    ↓
SQLite Database
```

This ensures:
- ✅ Business logic doesn't contain SQL
- ✅ Database operations are centralized
- ✅ Easy to test and mock
- ✅ Schema changes are localized

---

## Schema Change Procedure

When modifying the schema:

1. **Update `settings_repository.py`**
   - Add new `_create_*_table()` method
   - Add new `_*_table_exists()` check
   - Update `_tables_exist()` to include new check
   - Update `_create_tables()` to create new table

2. **Update version documentation** in this file

3. **Test with fresh database:**
   ```bash
   python reset_settings.py --full
   # Restart app
   ```

4. **Consider migration** if changing existing tables
   - Add migration code to handle existing data
   - Or document that users need to reset

5. **Update `reset_settings.py`** if needed
   - Add new table to `--full` option
   - Consider adding specific reset option

---

## Backup & Recovery

**Create Backup:**
```bash
cp ~/.FLASH\ for\ Anki/storage.db ~/storage.db.backup
```

**Restore Backup:**
```bash
cp ~/storage.db.backup ~/.FLASH\ for\ Anki/storage.db
```

**Automatic Backups:**

The reset utility creates automatic backups:
```bash
python reset_settings.py --api-keys
# Creates: storage_backup_20251116_215333.db
```

---

## Security Considerations

1. **Encryption Key Storage**
   - Stored in `settings` table as `encryption_key`
   - Base64 encoded Fernet key
   - Auto-generated if missing
   - **Do not share or commit this key**

2. **API Keys**
   - Always stored encrypted as BLOB
   - Never stored in plaintext
   - Decrypted only when needed

3. **Database Permissions**
   - Database file should be user-readable only
   - No group or world permissions

4. **Backup Security**
   - Backups contain encrypted API keys
   - Still protect backups like the original database

---

## Troubleshooting

### Can't find database
```bash
python reset_settings.py --info
```
Shows the expected path.

### Corrupt database
```bash
python reset_settings.py --full
```
Deletes and recreates everything.

### Wrong schema
```bash
rm ~/.FLASH\ for\ Anki/storage.db
# Restart app - will create new database
```

### Want to inspect manually
```bash
sqlite3 ~/.FLASH\ for\ Anki/storage.db
.tables
.schema settings
SELECT * FROM settings;
.quit
```
