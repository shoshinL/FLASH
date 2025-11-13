# UI Testing Guide for Multi-Provider Integration

This guide covers manual testing of the new provider management UI.

## Setup

1. **Build the frontend**:
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

2. **Run the application**:
   ```bash
   cd backend
   python index.py
   ```

## Test Scenarios

### 1. Provider Settings UI - Initial Load ✅

**Steps**:
1. Launch the application
2. Click the Settings button (gear icon)
3. Click the "Model Provider" tab

**Expected Results**:
- [ ] Settings modal opens properly
- [ ] Two tabs visible: "Model Provider" and "Anki Integration"
- [ ] "Model Provider" tab is selected by default
- [ ] Provider dropdown shows 5 options: OpenAI, Anthropic, Google (Gemini), OpenRouter, Ollama (Local)
- [ ] Current provider is selected (default: OpenAI)
- [ ] UI elements load without errors

**Screenshot**: Take a screenshot of the initial provider settings view

---

### 2. OpenAI Provider Configuration ✅

**Steps**:
1. Select "OpenAI" from provider dropdown
2. Enter your OpenAI API key in the API key field
3. Click "Set API Key" button
4. Wait for models to load
5. Select a model (e.g., "gpt-4o-mini")
6. Click "Apply Provider Configuration"

**Expected Results**:
- [ ] API key input field is visible (password field)
- [ ] Success message appears after setting API key
- [ ] Models dropdown populates with OpenAI models
- [ ] Models include: gpt-4o, gpt-4o-mini, o1, o3-mini
- [ ] Success message appears after applying configuration
- [ ] API key status shows masked key (e.g., "***xyz")

**Screenshot**: Take screenshots of:
- API key set success message
- Model selection dropdown
- Apply configuration success

---

### 3. Anthropic Provider Configuration ✅

**Steps**:
1. Select "Anthropic" from provider dropdown
2. Enter your Anthropic API key
3. Click "Set API Key"
4. Select "claude-3-5-haiku-20241022" model
5. Click "Apply Provider Configuration"

**Expected Results**:
- [ ] Previous provider's API key is cleared
- [ ] Anthropic API key field appears
- [ ] Models load successfully
- [ ] Models include Claude 3.5 Sonnet, Claude 3.5 Haiku, etc.
- [ ] Configuration saves successfully

---

### 4. Google (Gemini) Provider Configuration ✅

**Steps**:
1. Select "Google (Gemini)" from provider dropdown
2. Enter your Google AI API key
3. Set API key and select a model
4. Check for Gemini 2.0 models including thinking models

**Expected Results**:
- [ ] Google provider information displays correctly
- [ ] Models include: gemini-2.0-flash-exp, gemini-2.0-flash-thinking-exp-1219
- [ ] Thinking models are available in the list
- [ ] Configuration applies successfully

---

### 5. OpenRouter Provider Configuration ✅

**Steps**:
1. Select "OpenRouter" from provider dropdown
2. Enter your OpenRouter API key
3. Browse available models

**Expected Results**:
- [ ] OpenRouter description mentions "access to multiple AI models"
- [ ] Models list includes various providers (Anthropic, OpenAI, Google, etc.)
- [ ] Example models: anthropic/claude-3.5-sonnet, openai/gpt-4o, google/gemini-2.0-flash-exp

---

### 6. Ollama (Local) Provider Configuration ✅

**Steps**:
1. Select "Ollama (Local)" from provider dropdown
2. Observe the UI changes

**Expected Results**:
- [ ] API key section is NOT visible (Ollama doesn't need API key)
- [ ] Models dropdown shows locally installed Ollama models
- [ ] If Ollama is not running: Error message displays "Ollama is not running or no models are installed"
- [ ] If Ollama is running: List of installed models (e.g., llama3.2, mistral, codellama)
- [ ] Provider description mentions "runs LLM models locally"

**Test with Ollama Running**:
1. Start Ollama: `ollama serve` (in a separate terminal)
2. Install a model: `ollama pull llama3.2`
3. Refresh the provider settings
4. Verify model appears in dropdown

**Test with Ollama Not Running**:
1. Stop Ollama service
2. Select Ollama provider
3. Verify error message appears

---

### 7. API Key Persistence ✅

**Steps**:
1. Set API keys for OpenAI and Anthropic
2. Close the settings modal
3. Reopen settings
4. Switch between providers

**Expected Results**:
- [ ] Previously set API keys show as masked (***xyz)
- [ ] "Update Key" button shows checkmark (✓)
- [ ] Button text changes from "Set API Key" to "✓ Update Key"
- [ ] Each provider remembers its own API key

---

### 8. Model Selection Persistence ✅

**Steps**:
1. Select OpenAI provider with gpt-4o-mini model
2. Apply configuration
3. Close application
4. Restart application
5. Open settings

**Expected Results**:
- [ ] OpenAI is still selected as provider
- [ ] gpt-4o-mini is still selected as model
- [ ] Configuration persists across application restarts

---

### 9. Error Handling - Invalid API Key ✅

**Steps**:
1. Select OpenAI provider
2. Enter an invalid API key (e.g., "invalid-key-123")
3. Click "Set API Key"

**Expected Results**:
- [ ] Error message appears
- [ ] Models do not load
- [ ] UI remains functional (no crashes)
- [ ] Can correct the API key and try again

---

### 10. Error Handling - Network Issues ✅

**Steps**:
1. Disconnect from internet
2. Select a provider that requires network (OpenAI, Anthropic, etc.)
3. Try to load models

**Expected Results**:
- [ ] Error message displays: "Failed to fetch models"
- [ ] UI remains responsive
- [ ] Can retry after reconnecting

---

### 11. Tab Navigation ✅

**Steps**:
1. Open settings
2. Click between "Model Provider" and "Anki Integration" tabs
3. Make changes in each tab

**Expected Results**:
- [ ] Tabs switch smoothly
- [ ] Active tab is visually highlighted (green underline)
- [ ] Content changes correctly
- [ ] No layout issues or overlaps
- [ ] Settings in each tab are independent

---

### 12. Responsive Design ✅

**Steps**:
1. Resize the application window
2. Test at different widths

**Expected Results**:
- [ ] Settings modal adapts to window size
- [ ] Text remains readable
- [ ] Buttons don't overlap
- [ ] Scrolling works if content overflows

---

### 13. Provider Information Display ✅

**Steps**:
1. Select each provider one by one
2. Read the "About this provider" section

**Expected Results**:
- [ ] Each provider shows unique description
- [ ] Information is accurate and helpful
- [ ] OpenAI: Mentions GPT models, o1, o3-mini
- [ ] Anthropic: Mentions Claude, helpful/harmless/honest
- [ ] Google: Mentions Gemini, multimodal, thinking models
- [ ] OpenRouter: Mentions multiple models access
- [ ] Ollama: Mentions local execution, no API key

---

### 14. Success Messages and Feedback ✅

**Steps**:
1. Set an API key
2. Change model
3. Apply configuration

**Expected Results**:
- [ ] Success messages appear in green
- [ ] Messages auto-dismiss after ~3 seconds
- [ ] Messages slide in with animation
- [ ] Multiple operations show appropriate messages

---

### 15. Integration Test - Full Workflow ✅

**Steps**:
1. Open application
2. Go to Model Provider settings
3. Set up OpenAI with gpt-4o-mini
4. Go to Anki Integration tab
5. Set up Anki database, profile, and deck
6. Go to main Editor view
7. Upload a PDF
8. Generate flashcards
9. Verify flashcards are created

**Expected Results**:
- [ ] Provider configuration works end-to-end
- [ ] Flashcards generate using selected provider/model
- [ ] No errors during generation
- [ ] Flashcards are correctly formatted
- [ ] Can export to Anki successfully

---

### 16. Thinking Model Test (If Available) ✅

**Steps**:
1. Set up OpenAI provider
2. Select "o3-mini" model (or "o1")
3. Apply configuration
4. Generate flashcards from a PDF

**Expected Results**:
- [ ] Thinking model is selectable
- [ ] Flashcard generation completes without parsing errors
- [ ] Thinking traces are properly stripped
- [ ] Output quality is maintained
- [ ] No "Invalid JSON" errors

**Alternative with Google**:
1. Select Google provider
2. Choose "gemini-2.0-flash-thinking-exp-1219"
3. Generate flashcards
4. Verify thinking model works correctly

---

## Common Issues to Watch For

### Provider-Specific Issues
- [ ] **OpenAI**: Rate limiting with o1/o3-mini models
- [ ] **Anthropic**: Long initial response times
- [ ] **Google**: Some models may not be available in all regions
- [ ] **OpenRouter**: Requires credits, not just API key
- [ ] **Ollama**: Must be running locally, models must be pre-pulled

### UI Issues
- [ ] Dropdowns not populating
- [ ] Error messages not clearing
- [ ] Modal not closing properly
- [ ] Layout breaking at certain window sizes
- [ ] Buttons not responding

### Data Persistence Issues
- [ ] API keys not saving
- [ ] Model selection not persisting
- [ ] Settings reverting after restart

---

## Reporting Results

After completing the tests, create a summary with:

1. **Overall Status**: All passed / Some issues / Major problems
2. **Test Results**: Number of tests passed/failed
3. **Screenshots**: Key UI elements and any errors
4. **Issues Found**: Detailed description of any problems
5. **Browser/OS**: Your testing environment
6. **Suggestions**: Any UX improvements

### Screenshot Checklist
Please capture:
- [ ] Provider selection dropdown
- [ ] Each provider's configuration screen
- [ ] Success messages
- [ ] Error messages (if any occur)
- [ ] Ollama with models loaded
- [ ] Ollama with error (not running)
- [ ] API key status display
- [ ] Model selection dropdowns
- [ ] Tab navigation
- [ ] Complete settings modal view

---

## Quick Test (5 minutes)

If you're short on time, test these critical scenarios:

1. ✅ Open settings → See provider dropdown
2. ✅ Select OpenAI → Enter API key → See models
3. ✅ Select Ollama → Verify no API key field
4. ✅ Switch between providers → Verify UI updates
5. ✅ Apply configuration → Generate flashcards

This covers the core functionality!
