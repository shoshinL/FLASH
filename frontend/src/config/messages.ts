/**
 * User-Facing Messages Configuration
 *
 * Centralized location for all user-facing text strings.
 * This makes it easy to:
 * - Maintain consistent messaging
 * - Update copy without touching component code
 * - Prepare for future internationalization (i18n)
 */

// ============ Error Messages ============

export const ERRORS = {
  // Provider configuration
  PROVIDER_CONFIG_LOAD: "Failed to load provider configuration",
  PROVIDER_CONFIG_SAVE: "Failed to save provider configuration",

  // Model fetching
  MODELS_FETCH: "Failed to fetch available models",

  // API Keys
  API_KEY_SET: "Failed to set API key",
  API_KEY_DELETE: "Failed to delete API key",
  API_KEY_LOAD: "Failed to load API keys",
  API_KEY_EMPTY: "Please enter an API key",

  // Embedding configuration
  EMBEDDING_MODEL_SET: "Failed to set embedding model",
  EMBEDDING_CONFIG_SAVE: "Failed to save embedding configuration",

  // Thinking configuration
  THINKING_CONFIG_SAVE: "Failed to save thinking configuration",

  // Provider settings
  PROVIDER_SETTINGS_LOAD: "Failed to load provider settings",
} as const;

// ============ Success Messages ============

export const SUCCESS = {
  // Provider configuration
  PROVIDER_CONFIG_SAVED: "Provider configuration saved successfully!",
  MODEL_UPDATED: "Model updated successfully!",

  // API Keys
  API_KEY_SET: (providerName: string) => `${providerName} API key set successfully!`,
  API_KEY_DELETED: (providerName: string) => `${providerName} API key deleted successfully!`,

  // Embedding configuration
  EMBEDDING_MODEL_UPDATED: "Embedding model updated successfully!",
  EMBEDDING_CONFIG_SAVED: "Embedding configuration saved successfully!",
} as const;

// ============ Validation Messages ============

export const VALIDATION = {
  // API Key validation
  VALID_FORMAT: '✓ Valid format',
  VALID_LENGTH: '✓ Valid length',

  // Warnings
  OPENAI_KEY_PREFIX: '⚠️ OpenAI keys should start with "sk-"',
  OPENAI_KEY_LENGTH: '⚠️ OpenAI keys are typically longer',

  ANTHROPIC_KEY_PREFIX: '⚠️ Anthropic keys should start with "sk-ant-"',
  ANTHROPIC_KEY_LENGTH: '⚠️ Anthropic keys are typically longer',

  GOOGLE_KEY_LENGTH: '⚠️ Google API keys are typically longer',

  OPENROUTER_KEY_PREFIX: '⚠️ OpenRouter keys should start with "sk-or-"',
  OPENROUTER_KEY_LENGTH: '⚠️ OpenRouter keys are typically longer',

  GENERIC_KEY_SHORT: '⚠️ Key seems too short',
} as const;

// ============ Info & Help Messages ============

export const INFO = {
  // Ollama messages
  OLLAMA_NOT_RUNNING: (modelType: string) =>
    `⚠️ Ollama is not running or no ${modelType} are installed. Start Ollama with 'ollama serve' and install ${modelType}.`,

  OLLAMA_NO_MODELS_TITLE: (isEmbedding: boolean) =>
    `No Ollama ${isEmbedding ? 'embedding models' : 'models'} found.`,

  OLLAMA_INSTALL_PROMPT: (isEmbedding: boolean) =>
    `Install ${isEmbedding ? 'embedding models' : 'models'} using these commands:`,

  // Provider requirements
  API_KEY_REQUIRED: (providerName: string) =>
    `Please set an API key for ${providerName} first`,

  API_KEY_REQUIRED_TAB: (providerName: string) =>
    `⚠️ ${providerName} requires an API key. Please set it in the API Keys tab.`,

  // Model selection
  NO_MODELS_AVAILABLE: (modelType: string = 'models') =>
    `No ${modelType} available`,

  SELECT_MODEL: 'Select a model',

  // API Keys tab
  API_KEYS_DESCRIPTION:
    'Manage your API keys for different providers. API keys are stored securely and required for providers like OpenAI, Anthropic, Google, and OpenRouter. Ollama runs locally and doesn\'t require an API key.',

  NO_API_KEY_NEEDED: 'No API key needed',
  API_KEY_SET: 'API Key Set',
  API_KEY_NOT_SET: 'Not Set',

  LOCAL_PROVIDER: 'This provider runs locally and doesn\'t require an API key.',
} as const;

// ============ Button Labels ============

export const BUTTONS = {
  SET_API_KEY: 'Set API Key',
  UPDATE_API_KEY: '✓ Update Key',
  SAVE_CONFIGURATION: 'Save Configuration',
  DELETE_API_KEY_TITLE: 'Delete API key',
} as const;

// ============ Field Labels & Tooltips ============

export const LABELS = {
  PROVIDER: 'Provider',
  MODEL: 'Model',
  API_KEY: 'API Key',
  THINKING_BUDGET: 'Thinking Budget',
  REASONING_EFFORT: 'Reasoning Effort',
} as const;

export const TOOLTIPS = {
  // Provider selection
  LLM_PROVIDER: 'Select your LLM provider (OpenAI, Anthropic, Google, etc.)',
  EMBEDDING_PROVIDER: 'Embeddings convert text to vectors for similarity search and document retrieval',

  // Model selection
  MODEL_SELECT: 'Choose the specific model to use for generation',
  EMBEDDING_MODEL_SELECT: 'Choose the specific embedding model to use',

  // API Keys
  API_KEY: (providerName: string) => `Your ${providerName} API key - stored securely`,

  // Thinking configuration
  THINKING_ENABLED: 'Allow the model to spend more time reasoning before responding (if supported). Works with: OpenAI o1/o3/o4 models, all Claude models, Gemini *-thinking-* models, and some Ollama models (qwen, cogito). Improves quality but increases cost.',
  THINKING_BUDGET: 'Number of tokens allocated for thinking - higher values allow deeper reasoning but cost more (Claude models only)',
  REASONING_EFFORT: 'Controls how much computational effort the model uses for reasoning (OpenAI o-series models only)',
} as const;
