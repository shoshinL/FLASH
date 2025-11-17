# Tests Directory

This directory contains all backend tests.

## Test Files

- `test_config_template.py` - Configuration template tests
- `test_providers.py` - LLM provider tests
- `test_refactoring.py` - Refactoring verification tests

## Running Tests

```bash
cd backend
python -m pytest tests/
```

Or run individual test files:
```bash
python -m pytest tests/test_providers.py
```
