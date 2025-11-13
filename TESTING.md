# Testing Guide for Multi-Provider Integration

This guide covers how to test the new multi-provider LLM integration feature.

## Quick Start

### Backend Testing (Automated)

1. **Setup test configuration**:
   ```bash
   cd backend
   cp test_config_template.py test_config_local.py
   ```

2. **Add your API keys** to `test_config_local.py`:
   ```python
   API_KEYS = {
       "openai": "sk-your-key-here",
       "anthropic": "sk-ant-your-key-here",
       "google": "your-google-key-here",
       "openrouter": "your-openrouter-key-here",
       "ollama": None,  # No key needed
   }
   ```

3. **Run the test suite**:
   ```bash
   python test_providers.py
   ```

4. **Review results**:
   - `test_report.md` - Human-readable report
   - `test_results.json` - Machine-readable results

### Frontend/UI Testing (Manual)

Follow the detailed guide in `UI_TEST_GUIDE.md`.

---

## Backend Test Suite

### What Gets Tested

The automated backend test suite (`test_providers.py`) tests 7 key areas for each provider:

1. **Provider Initialization** ✅
   - Tests that the provider class can be instantiated
   - Verifies model configuration

2. **API Key Validation** ✅
   - Tests that API keys are validated correctly
   - Verifies connection to provider APIs

3. **Model Listing** ✅
   - Tests fetching available models
   - Verifies model list is not empty

4. **Basic LLM Call** ✅
   - Tests simple text generation
   - Verifies the provider responds correctly

5. **JSON Parsing** ✅
   - Tests structured output generation
   - Verifies JSON parser works with provider

6. **Thinking Trace Removal** ✅
   - Tests the thinking trace stripping logic
   - Verifies XML tags and JSON fields are removed

7. **Thinking Model Support** ✅ (Optional)
   - Tests o1, o3-mini, Gemini 2.0 Thinking models
   - Verifies thinking-aware parser works correctly

### Test Configuration

Edit `test_config_local.py` to customize:

```python
# Skip expensive models
TEST_SETTINGS = {
    "skip_expensive": True,  # Skip o1/o3 if True
    "test_thinking_models": False,  # Enable thinking model tests
    "timeout": 30,  # API call timeout
}

# Choose which models to test
TEST_MODELS = {
    "openai": "gpt-4o-mini",  # Use cheaper models
    "anthropic": "claude-3-5-haiku-20241022",
}
```

### Running Specific Tests

To run tests for only one provider, modify `test_providers.py`:

```python
# At the bottom of run_all_tests()
providers = ["openai"]  # Test only OpenAI
# providers = ["ollama"]  # Test only Ollama
```

### Understanding Test Results

#### Test Report Format

The markdown report (`test_report.md`) includes:

- **Summary by Provider**: Pass/fail rates for each provider
- **Detailed Test Results**: Individual test outcomes with timing
- **Recommendations**: Action items for failed tests

#### Example Report Section

```markdown
### ✅ OPENAI
- Total Tests: 7
- Passed: 7 ✅
- Failed: 0 ❌
- Skipped: 0 ⏭️
- Pass Rate: 100.0%

### ⚠️ ANTHROPIC
- Total Tests: 7
- Passed: 5 ✅
- Failed: 1 ❌
- Skipped: 1 ⏭️
- Pass Rate: 71.4%
```

#### Common Test Failures

**No API key provided**:
```
Status: SKIP
Reason: No API key provided
```
→ Add your API key to `test_config_local.py`

**Invalid API key**:
```
Status: FAIL
Error: Authentication failed
```
→ Check your API key is correct and active

**Ollama not running**:
```
Status: FAIL
Error: Connection refused
```
→ Start Ollama: `ollama serve`

**Rate limit exceeded**:
```
Status: FAIL
Error: Rate limit exceeded
```
→ Wait a few minutes or use a different model

---

## UI Testing

### Prerequisites

1. Build the frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

2. Run the application:
   ```bash
   cd backend
   python index.py
   ```

### Critical Test Scenarios

Follow `UI_TEST_GUIDE.md` for detailed steps. Key scenarios:

1. **Provider Selection** - Switch between providers
2. **API Key Management** - Set and update keys
3. **Model Selection** - Choose and apply models
4. **Ollama Integration** - Test local models
5. **Persistence** - Settings survive restarts
6. **Error Handling** - Invalid keys, network issues
7. **End-to-End** - Generate flashcards with new provider

### UI Testing Checklist

Quick checklist for essential tests:

- [ ] Provider dropdown shows all 5 providers
- [ ] Can set API keys for each provider
- [ ] Models load correctly for each provider
- [ ] Ollama shows "no API key needed"
- [ ] Configuration persists after restart
- [ ] Error messages display properly
- [ ] Can generate flashcards with new provider
- [ ] Thinking models work without errors

---

## Test Data

### Sample API Keys (for testing structure, not real)

```python
# DO NOT commit real keys!
API_KEYS = {
    "openai": "sk-proj-xxxxxxxxxxxxxxxxxxxxx",
    "anthropic": "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx",
    "google": "AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXX",
    "openrouter": "sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx",
}
```

### Test Documents

For integration testing, use these sample PDFs:

1. **Short document** (1 page) - Quick testing
2. **Medium document** (5-10 pages) - Standard testing
3. **Long document** (20+ pages) - Stress testing

The test suite includes a built-in sample chunk about machine learning.

---

## Troubleshooting

### Backend Tests

**Problem**: `ImportError: No module named 'langchain_anthropic'`
```bash
pip install -r requirements.txt
```

**Problem**: Tests hang or timeout
- Check internet connection
- Increase timeout in `test_config_local.py`
- Check provider status pages

**Problem**: All tests fail for one provider
- Verify API key is valid
- Check provider API status
- Try a different model

### UI Tests

**Problem**: Settings modal won't open
- Check browser console for errors
- Verify frontend build succeeded
- Restart the application

**Problem**: Models don't load
- Check network tab in browser devtools
- Verify API key is set
- Check backend logs for errors

**Problem**: Configuration doesn't persist
- Check database permissions
- Verify settings file location
- Check backend logs

---

## Reporting Test Results

### For Backend Tests

Send the following:

1. **test_report.md** - Full report
2. **test_results.json** - Raw data
3. **Environment info**:
   ```
   OS: [Your OS]
   Python: [Version]
   Internet: [Connection type]
   ```

### For UI Tests

Provide:

1. **Screenshots** of key scenarios
2. **Test checklist** with results
3. **Browser info**: Name and version
4. **Any error messages** from console
5. **Video** if showing a bug (optional)

### Template

```markdown
## Test Results Summary

**Date**: 2025-XX-XX
**Tester**: [Your name]
**Branch**: claude/multi-provider-integration-011CV5UHABvJCdzf7V3xPG3S

### Backend Tests
- Total: X tests
- Passed: X
- Failed: X
- Skipped: X

Providers tested: [List]
Issues found: [Description]

### UI Tests
- Scenarios tested: X/16
- Critical issues: [None/List]
- Minor issues: [None/List]

Screenshots attached: [Yes/No]

### Overall Assessment
[Working well / Minor issues / Major problems]

### Recommendations
[Any suggestions for improvement]
```

---

## CI/CD Integration (Future)

To integrate these tests into CI/CD:

```yaml
# .github/workflows/test.yml
name: Test Multi-Provider Integration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Create test config
        run: |
          cd backend
          cp test_config_template.py test_config_local.py
          # Add secrets from GitHub
      - name: Run tests
        run: python backend/test_providers.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: test-results
          path: |
            backend/test_report.md
            backend/test_results.json
```

---

## Quick Reference

### Files

- `backend/test_providers.py` - Main test suite
- `backend/test_config_template.py` - Config template
- `backend/test_config_local.py` - Your config (gitignored)
- `backend/test_report.md` - Generated report
- `backend/test_results.json` - Generated results
- `UI_TEST_GUIDE.md` - UI testing guide
- `TESTING.md` - This file

### Commands

```bash
# Setup
cp backend/test_config_template.py backend/test_config_local.py

# Run backend tests
python backend/test_providers.py

# Run application for UI testing
python backend/index.py

# Build frontend
cd frontend && npm run build
```

### Provider Status Pages

Check if providers are having issues:

- OpenAI: https://status.openai.com/
- Anthropic: https://status.anthropic.com/
- Google: https://status.cloud.google.com/
- OpenRouter: https://openrouter.ai/status

---

## Need Help?

If you encounter issues:

1. Check this guide first
2. Review error messages carefully
3. Search existing issues on GitHub
4. Create a new issue with test results attached

Include in your issue:
- Test report (`test_report.md`)
- Screenshots (for UI issues)
- System information
- Steps to reproduce
