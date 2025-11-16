# How to Reset FLASH Settings

## Quick Fix for Decryption Errors

If you're seeing errors like:
```
ERROR - Failed to decrypt API key for anthropic
ERROR - Failed to decrypt API key for openai
```

**Solution: Reset your API keys**

```bash
cd backend
python reset_settings.py --api-keys
```

This will:
1. Create a backup of your database
2. Delete all encrypted API keys
3. Delete the encryption key (will be regenerated)
4. You'll need to re-enter your API keys in the app

---

## Other Reset Options

### Check Current Settings
```bash
python reset_settings.py --info
```

Shows what's in your database without changing anything.

### Reset Specific Parts

**Reset Anki settings only:**
```bash
python reset_settings.py --anki
```

**Reset provider configuration:**
```bash
python reset_settings.py --providers
```

**Reset thinking configuration:**
```bash
python reset_settings.py --thinking
```

**Reset multiple things at once:**
```bash
python reset_settings.py --api-keys --providers --thinking
```

### Nuclear Option (Fresh Start)

**Delete everything:**
```bash
python reset_settings.py --full
```

⚠️ This deletes the entire database. Use with caution!

---

## Dry Run Mode

Test what will be deleted without actually deleting:

```bash
python reset_settings.py --api-keys --dry-run
```

---

## Backup

By default, a backup is created before any reset:
- Location: Same folder as `storage.db`
- Format: `storage_backup_YYYYMMDD_HHMMSS.db`

Skip backup (not recommended):
```bash
python reset_settings.py --api-keys --no-backup
```

---

## Where is the Database?

- **Linux:** `~/.FLASH for Anki/storage.db`
- **macOS:** `~/Library/Application Support/FLASH for Anki/storage.db`
- **Windows:** `%APPDATA%\FLASH for Anki\storage.db`

---

## Common Scenarios

### Scenario 1: Decryption Errors
**Problem:** Can't decrypt API keys after update
**Solution:**
```bash
python reset_settings.py --api-keys
```
Then re-enter your API keys in the app.

### Scenario 2: Wrong Anki Database
**Problem:** Can't find Anki profiles/decks
**Solution:**
```bash
python reset_settings.py --anki
```
Then reconfigure Anki path in the app.

### Scenario 3: Provider Issues
**Problem:** Wrong provider selected or can't switch providers
**Solution:**
```bash
python reset_settings.py --providers
```
Then reconfigure providers in the app.

### Scenario 4: Start Fresh
**Problem:** Something is broken, want to start over
**Solution:**
```bash
python reset_settings.py --full
```
Everything will be reset. Reconfigure in the app.

---

## Need Help?

Run the help command:
```bash
python reset_settings.py --help
```

Or check the database info:
```bash
python reset_settings.py --info
```
