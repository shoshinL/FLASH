import { useState, useEffect } from "react";
import "./ProviderSettings.css";

interface ProviderConfig {
  provider: string;
  model: string | null;
  api_key_set: boolean;
}

interface EmbeddingConfig {
  provider: string;
  model: string | null;
  api_key_set: boolean;
  success: boolean;
}

interface ThinkingConfig {
  enabled: boolean;
  budget_tokens: number;
  effort: string;
  summary: string;
}

interface ProvidersResponse {
  providers: string[];
  success?: boolean;
}

interface ModelsResponse {
  models: string[];
  success: boolean;
  error?: string;
}

interface ApiKeysStatusResponse {
  api_keys: Record<string, string>;
  success: boolean;
}

const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
  openai: "OpenAI",
  anthropic: "Anthropic",
  google: "Google (Gemini)",
  openrouter: "OpenRouter",
  ollama: "Ollama (Local)"
};

// Model grouping configuration
const MODEL_GROUPS: Record<string, Record<string, string[]>> = {
  openai: {
    "GPT-4 Models (Latest)": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    "GPT-4 Models (Legacy)": ["gpt-4", "gpt-4-32k"],
    "GPT-3.5 Models": ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    "Reasoning Models": ["o1", "o1-mini", "o1-preview", "o3-mini"]
  },
  anthropic: {
    "Claude 3.5 Models": ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-5-haiku-20241022"],
    "Claude 3 Models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
  },
  google: {
    "Gemini 2.0 Models": ["gemini-2.0-flash-exp", "gemini-2.0-flash-thinking-exp"],
    "Gemini 1.5 Models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
    "Gemini 1.0 Models": ["gemini-1.0-pro"]
  },
  ollama: {
    "Reasoning Models": ["deepseek-r1", "cogito", "qwq"],
    "Large Models (>7B)": ["llama3.2:70b", "llama3.1:70b", "qwen2.5:14b", "mixtral"],
    "Medium Models (7B)": ["llama3.2:7b", "llama3.1:7b", "mistral", "qwen2.5:7b"],
    "Small Models (<7B)": ["llama3.2:3b", "llama3.2:1b", "deepseek-r1:1.5b", "phi3", "gemma2:2b"]
  }
};

const EMBEDDING_MODEL_GROUPS: Record<string, Record<string, string[]>> = {
  openai: {
    "OpenAI Embeddings": ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"]
  },
  google: {
    "Gecko Embeddings": ["text-embedding-004", "text-embedding-005"]
  },
  ollama: {
    "Embedding Models": ["snowflake-arctic-embed2", "nomic-embed-text", "mxbai-embed-large", "all-minilm"]
  }
};

interface ProviderSettingsProps {
  mode: "llm" | "embedding" | "api_keys";
}

export function ProviderSettings({ mode }: ProviderSettingsProps) {
  // LLM Configuration State
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [currentProvider, setCurrentProvider] = useState<string>("openai");
  const [currentModel, setCurrentModel] = useState<string | null>(null);
  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [apiKeyInput, setApiKeyInput] = useState<string>("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [modelLoading, setModelLoading] = useState<boolean>(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Embedding Configuration State
  const [embeddingProviders, setEmbeddingProviders] = useState<string[]>([]);
  const [currentEmbeddingProvider, setCurrentEmbeddingProvider] = useState<string>("openai");
  const [currentEmbeddingModel, setCurrentEmbeddingModel] = useState<string | null>(null);
  const [availableEmbeddingModels, setAvailableEmbeddingModels] = useState<string[]>([]);
  const [embeddingModelLoading, setEmbeddingModelLoading] = useState<boolean>(false);
  const [embeddingError, setEmbeddingError] = useState<string | null>(null);
  const [embeddingSuccessMessage, setEmbeddingSuccessMessage] = useState<string | null>(null);

  // Thinking/Reasoning Configuration State
  const [thinkingEnabled, setThinkingEnabled] = useState<boolean>(false);
  const [thinkingBudget, setThinkingBudget] = useState<number>(2000);
  const [reasoningEffort, setReasoningEffort] = useState<string>("medium");
  const [reasoningSummary, setReasoningSummary] = useState<string>("auto");
  const [providerSupportsThinking, setProviderSupportsThinking] = useState<boolean>(false);

  // Validation state
  const [apiKeyValidation, setApiKeyValidation] = useState<string | null>(null);

  useEffect(() => {
    fetchProviderData();
  }, []);

  useEffect(() => {
    if (currentProvider) {
      fetchAvailableModels(currentProvider);
    }
  }, [currentProvider]);

  useEffect(() => {
    if (currentEmbeddingProvider) {
      fetchAvailableEmbeddingModels(currentEmbeddingProvider);
    }
  }, [currentEmbeddingProvider]);

  useEffect(() => {
    // Check if provider/model supports thinking whenever they change
    if (currentProvider && currentModel) {
      checkThinkingSupport();
    }
  }, [currentProvider, currentModel]);

  useEffect(() => {
    // Fetch thinking configuration on load
    fetchThinkingConfig();
  }, []);

  const fetchProviderData = async () => {
    setLoading(true);
    try {
      // Fetch available LLM providers
      const providersResp: unknown = await window.pywebview.api.get_available_providers();
      if (isProvidersResponse(providersResp)) {
        setAvailableProviders(providersResp.providers);
      }

      // Fetch current LLM provider config
      const configResp: unknown = await window.pywebview.api.get_provider_config();
      if (isProviderConfig(configResp)) {
        setCurrentProvider(configResp.provider);
        setCurrentModel(configResp.model);
      }

      // Fetch API keys status
      const keysResp: unknown = await window.pywebview.api.get_provider_api_keys_status();
      if (isApiKeysStatusResponse(keysResp)) {
        setApiKeys(keysResp.api_keys);
      }

      // Fetch available embedding providers
      const embeddingProvidersResp: unknown = await window.pywebview.api.get_embedding_providers();
      if (isProvidersResponse(embeddingProvidersResp)) {
        setEmbeddingProviders(embeddingProvidersResp.providers);
      }

      // Fetch current embedding config
      const embeddingConfigResp: unknown = await window.pywebview.api.get_embedding_config();
      if (isEmbeddingConfig(embeddingConfigResp)) {
        setCurrentEmbeddingProvider(embeddingConfigResp.provider);
        setCurrentEmbeddingModel(embeddingConfigResp.model);
      }

      setError(null);
      setEmbeddingError(null);
    } catch (err) {
      console.error("Error fetching provider data:", err);
      setError("Failed to load provider settings");
    } finally {
      setLoading(false);
    }
  };

  const fetchAvailableModels = async (provider: string) => {
    setModelLoading(true);
    try {
      const response: unknown = await window.pywebview.api.get_available_models(provider);
      if (isModelsResponse(response)) {
        if (response.success) {
          setAvailableModels(response.models);
          setError(null);
        } else {
          setAvailableModels([]);
          if (provider === 'ollama') {
            setError("⚠️ Ollama is not running or no models are installed. Start Ollama with 'ollama serve' and install models.");
          } else {
            setError(response.error || "Failed to fetch models");
          }
        }
      }
    } catch (err) {
      console.error("Error fetching models:", err);
      setAvailableModels([]);
      setError("Failed to fetch available models");
    } finally {
      setModelLoading(false);
    }
  };

  const fetchAvailableEmbeddingModels = async (provider: string) => {
    setEmbeddingModelLoading(true);
    try {
      const response: unknown = await window.pywebview.api.get_available_embedding_models(provider);
      if (isModelsResponse(response)) {
        if (response.success) {
          setAvailableEmbeddingModels(response.models);
          setEmbeddingError(null);
        } else {
          setAvailableEmbeddingModels([]);
          if (provider === 'ollama') {
            setEmbeddingError("⚠️ Ollama is not running or no embedding models are installed. Start Ollama with 'ollama serve' and install embedding models.");
          } else {
            setEmbeddingError(response.error || "Failed to fetch embedding models");
          }
        }
      }
    } catch (err) {
      console.error("Error fetching embedding models:", err);
      setAvailableEmbeddingModels([]);
      setEmbeddingError("Failed to fetch available embedding models");
    } finally {
      setEmbeddingModelLoading(false);
    }
  };

  const handleProviderChange = async (provider: string) => {
    setCurrentProvider(provider);
    setCurrentModel(null);
    setApiKeyInput("");
    setSuccessMessage(null);
    await fetchAvailableModels(provider);
  };

  const handleModelChange = async (model: string) => {
    setCurrentModel(model);
    try {
      await window.pywebview.api.set_provider_config(currentProvider, model);
      setSuccessMessage("Model updated successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error("Error setting model:", err);
      setError("Failed to set model");
    }
  };

  const handleSetApiKey = async () => {
    if (!apiKeyInput.trim()) {
      setError("Please enter an API key");
      return;
    }

    try {
      const response: unknown = await window.pywebview.api.set_provider_api_key(
        currentProvider,
        apiKeyInput
      );

      if (
        typeof response === "object" &&
        response !== null &&
        "success" in response &&
        response.success
      ) {
        // Refresh API keys status
        const keysResp: unknown = await window.pywebview.api.get_provider_api_keys_status();
        if (isApiKeysStatusResponse(keysResp)) {
          setApiKeys(keysResp.api_keys);
        }

        setApiKeyInput("");
        setSuccessMessage(`${PROVIDER_DISPLAY_NAMES[currentProvider]} API key set successfully!`);
        setTimeout(() => setSuccessMessage(null), 3000);
        setError(null);

        // Refresh models after setting API key
        await fetchAvailableModels(currentProvider);
      } else {
        setError("Failed to set API key");
      }
    } catch (err) {
      console.error("Error setting API key:", err);
      setError("Failed to set API key");
    }
  };

  const handleApplyProvider = async () => {
    try {
      await window.pywebview.api.set_provider_config(currentProvider, currentModel);
      setSuccessMessage("Provider configuration saved successfully!");
      setTimeout(() => setSuccessMessage(null), 3000);
      setError(null);
    } catch (err) {
      console.error("Error applying provider config:", err);
      setError("Failed to save provider configuration");
    }
  };

  const handleEmbeddingProviderChange = async (provider: string) => {
    setCurrentEmbeddingProvider(provider);
    setCurrentEmbeddingModel(null);
    setEmbeddingSuccessMessage(null);
    await fetchAvailableEmbeddingModels(provider);
  };

  const handleEmbeddingModelChange = async (model: string) => {
    setCurrentEmbeddingModel(model);
    try {
      const response: unknown = await window.pywebview.api.set_embedding_config(currentEmbeddingProvider, model);
      if (typeof response === "object" && response !== null && "success" in response && response.success) {
        setEmbeddingSuccessMessage("Embedding model updated successfully!");
        setTimeout(() => setEmbeddingSuccessMessage(null), 3000);
      } else {
        setEmbeddingError("Failed to set embedding model");
      }
    } catch (err) {
      console.error("Error setting embedding model:", err);
      setEmbeddingError("Failed to set embedding model");
    }
  };

  const handleApplyEmbedding = async () => {
    try {
      const response: unknown = await window.pywebview.api.set_embedding_config(currentEmbeddingProvider, currentEmbeddingModel);
      if (typeof response === "object" && response !== null && "success" in response && response.success) {
        setEmbeddingSuccessMessage("Embedding configuration saved successfully!");
        setTimeout(() => setEmbeddingSuccessMessage(null), 3000);
        setEmbeddingError(null);
      } else {
        const errorMsg = (typeof response === "object" && response !== null && "error" in response)
          ? String(response.error)
          : "Failed to save embedding configuration";
        setEmbeddingError(errorMsg);
      }
    } catch (err) {
      console.error("Error applying embedding config:", err);
      setEmbeddingError("Failed to save embedding configuration");
    }
  };

  const requiresApiKey = (provider: string): boolean => {
    return provider !== "ollama";
  };

  const hasApiKey = (provider: string): boolean => {
    return !!apiKeys[provider];
  };

  const validateApiKey = (provider: string, key: string): string | null => {
    if (!key.trim()) {
      return null;
    }

    const trimmedKey = key.trim();

    // Basic validation patterns for different providers
    switch (provider) {
      case 'openai':
        if (!trimmedKey.startsWith('sk-')) {
          return '⚠️ OpenAI keys should start with "sk-"';
        }
        if (trimmedKey.length < 40) {
          return '⚠️ OpenAI keys are typically longer';
        }
        return '✓ Valid format';

      case 'anthropic':
        if (!trimmedKey.startsWith('sk-ant-')) {
          return '⚠️ Anthropic keys should start with "sk-ant-"';
        }
        if (trimmedKey.length < 40) {
          return '⚠️ Anthropic keys are typically longer';
        }
        return '✓ Valid format';

      case 'google':
        if (trimmedKey.length < 30) {
          return '⚠️ Google API keys are typically longer';
        }
        return '✓ Valid format';

      case 'openrouter':
        if (!trimmedKey.startsWith('sk-or-')) {
          return '⚠️ OpenRouter keys should start with "sk-or-"';
        }
        if (trimmedKey.length < 40) {
          return '⚠️ OpenRouter keys are typically longer';
        }
        return '✓ Valid format';

      default:
        return trimmedKey.length > 20 ? '✓ Valid length' : '⚠️ Key seems too short';
    }
  };

  const handleApiKeyInputChange = (provider: string, key: string) => {
    setApiKeyInput(key);
    const validation = validateApiKey(provider, key);
    setApiKeyValidation(validation);
  };

  const handleDeleteApiKey = async (provider: string) => {
    try {
      const response: unknown = await window.pywebview.api.delete_provider_api_key(provider);

      if (
        typeof response === "object" &&
        response !== null &&
        "success" in response &&
        response.success
      ) {
        // Refresh API keys status
        const keysResp: unknown = await window.pywebview.api.get_provider_api_keys_status();
        if (isApiKeysStatusResponse(keysResp)) {
          setApiKeys(keysResp.api_keys);
        }

        setSuccessMessage(`${PROVIDER_DISPLAY_NAMES[provider]} API key deleted successfully!`);
        setTimeout(() => setSuccessMessage(null), 3000);
        setError(null);

        // Refresh models for the current provider if it matches
        if (currentProvider === provider) {
          await fetchAvailableModels(provider);
        }
        if (currentEmbeddingProvider === provider) {
          await fetchAvailableEmbeddingModels(provider);
        }
      } else {
        setError("Failed to delete API key");
      }
    } catch (err) {
      console.error("Error deleting API key:", err);
      setError("Failed to delete API key");
    }
  };

  const estimateThinkingCost = (tokens: number): string => {
    // Rough cost estimates (these are approximate and may vary)
    const costPerMillionTokens = 4.0; // Example: $4/million tokens for thinking
    const cost = (tokens / 1000000) * costPerMillionTokens;
    return cost < 0.01 ? '< $0.01' : `~$${cost.toFixed(2)}`;
  };

  const groupModels = (provider: string, models: string[], isEmbedding: boolean = false) => {
    const groups = isEmbedding ? EMBEDDING_MODEL_GROUPS : MODEL_GROUPS;
    const providerGroups = groups[provider];

    if (!providerGroups) {
      // No grouping config for this provider - return all as "Other Models"
      return { "Other Models": models };
    }

    const grouped: Record<string, string[]> = {};
    const ungrouped: string[] = [];

    // First, categorize models into their groups
    for (const model of models) {
      let found = false;
      for (const [groupName, groupModels] of Object.entries(providerGroups)) {
        // Check if model matches any pattern in the group
        if (groupModels.some(pattern =>
          model === pattern ||
          model.startsWith(pattern.replace(':latest', '')) ||
          model.includes(pattern)
        )) {
          if (!grouped[groupName]) {
            grouped[groupName] = [];
          }
          grouped[groupName].push(model);
          found = true;
          break;
        }
      }
      if (!found) {
        ungrouped.push(model);
      }
    }

    // Add ungrouped models to "Other Models" if any exist
    if (ungrouped.length > 0) {
      grouped["Other Models"] = ungrouped;
    }

    return grouped;
  };

  const fetchThinkingConfig = async () => {
    try {
      const response: unknown = await window.pywebview.api.get_thinking_config();
      if (isThinkingConfig(response)) {
        setThinkingEnabled(response.enabled);
        setThinkingBudget(response.budget_tokens);
        setReasoningEffort(response.effort);
        setReasoningSummary(response.summary);
      }
    } catch (err) {
      console.error("Error fetching thinking config:", err);
    }
  };

  const checkThinkingSupport = async () => {
    try {
      const response: unknown = await window.pywebview.api.check_thinking_support(currentProvider, currentModel);
      if (typeof response === "object" && response !== null && "supports_thinking" in response) {
        setProviderSupportsThinking(Boolean(response.supports_thinking));
      }
    } catch (err) {
      console.error("Error checking thinking support:", err);
      setProviderSupportsThinking(false);
    }
  };

  const handleThinkingConfigChange = async (updates: Partial<ThinkingConfig>) => {
    const newConfig = {
      enabled: thinkingEnabled,
      budget_tokens: thinkingBudget,
      effort: reasoningEffort,
      summary: reasoningSummary,
      ...updates
    };

    // Update local state
    if ('enabled' in updates) setThinkingEnabled(updates.enabled!);
    if ('budget_tokens' in updates) setThinkingBudget(updates.budget_tokens!);
    if ('effort' in updates) setReasoningEffort(updates.effort!);
    if ('summary' in updates) setReasoningSummary(updates.summary!);

    // Save to backend
    try {
      await window.pywebview.api.set_thinking_config(newConfig);
      // Silently save without showing success message
    } catch (err) {
      console.error("Error saving thinking config:", err);
      setError("Failed to save thinking configuration");
    }
  };

  if (loading) {
    return (
      <div className="provider-settings-container">
        <div className="skeleton skeleton-title"></div>
        <div className="skeleton-section">
          <div className="skeleton skeleton-text" style={{ width: '20%', marginBottom: '10px' }}></div>
          <div className="skeleton skeleton-select"></div>
        </div>
        <div className="skeleton-section">
          <div className="skeleton skeleton-text" style={{ width: '15%', marginBottom: '10px' }}></div>
          <div className="skeleton skeleton-select"></div>
        </div>
        <div className="skeleton-section">
          <div className="skeleton skeleton-button"></div>
        </div>
      </div>
    );
  }

  // Render LLM Model settings
  if (mode === "llm") {
    return (
      <div className="provider-settings-container">
        <h3>Language Model</h3>

        {error && <div className="error-message">{error}</div>}
        {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Model Provider Selection */}
      <div className="settings-item">
        <label>
          Provider
          <span className="info-icon" data-tooltip="Select your LLM provider (OpenAI, Anthropic, Google, etc.)">ℹ</span>
        </label>
        <select
          value={currentProvider}
          onChange={(e) => handleProviderChange(e.target.value)}
          className="provider-select"
        >
          {availableProviders.map((provider) => (
            <option
              key={provider}
              value={provider}
              disabled={requiresApiKey(provider) && !hasApiKey(provider)}
            >
              {PROVIDER_DISPLAY_NAMES[provider] || provider}
              {requiresApiKey(provider) && !hasApiKey(provider) ? ' (API key required)' : ''}
            </option>
          ))}
        </select>
      </div>


      {/* Model Selection */}
      <div className="settings-item">
        <label>
          Model
          <span className="info-icon" data-tooltip="Choose the specific model to use for generation">ℹ</span>
        </label>
        {modelLoading ? (
          <div className="skeleton skeleton-select"></div>
        ) : availableModels.length > 0 ? (
          <select
            value={currentModel || ""}
            onChange={(e) => handleModelChange(e.target.value)}
            className="model-select"
          >
            <option value="" disabled>
              Select a model
            </option>
            {Object.entries(groupModels(currentProvider, availableModels, false)).map(([groupName, models]) => (
              <optgroup key={groupName} label={groupName}>
                {models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        ) : (
          <div className="no-models">
            {currentProvider === 'ollama' ? (
              <div>
                <strong>No Ollama models found.</strong>
                <br />
                Install models using these commands:
                <br />
                <code style={{ display: 'block', marginTop: '8px', fontSize: '12px' }}>
                  ollama pull llama3.2<br />
                  ollama pull deepseek-r1:1.5b<br />
                  ollama pull qwen2.5:7b
                </code>
              </div>
            ) : requiresApiKey(currentProvider) && !hasApiKey(currentProvider) ? (
              'Please set an API key first'
            ) : (
              'No models available'
            )}
          </div>
        )}
      </div>

      {/* Thinking/Reasoning Configuration */}
      {providerSupportsThinking && (
        <>
          {/* Enable/Disable Toggle */}
          <div className="settings-item checkbox-item">
            <label>
              <input
                type="checkbox"
                checked={thinkingEnabled}
                onChange={(e) => handleThinkingConfigChange({ enabled: e.target.checked })}
              />
              <span>Enable extended thinking/reasoning</span>
              <span className="info-icon" data-tooltip="Allow the model to spend more time reasoning before responding - improves quality but increases cost">ℹ</span>
            </label>
          </div>

          {thinkingEnabled && (
            <>
              {/* Claude: Budget Tokens */}
              {currentProvider === 'anthropic' && (
                <div className="settings-item">
                  <label>
                    Thinking Budget
                    <span className="info-icon" data-tooltip="Number of tokens allocated for thinking - higher values allow deeper reasoning but cost more">ℹ</span>
                  </label>
                  <input
                    type="number"
                    value={thinkingBudget}
                    onChange={(e) => handleThinkingConfigChange({ budget_tokens: Number(e.target.value) })}
                    min={500}
                    max={10000}
                    step={500}
                    className="thinking-input"
                  />
                  <div style={{ marginTop: '8px', fontSize: '13px', color: '#666' }}>
                    <span className="input-unit">{thinkingBudget} tokens</span>
                    <span style={{ marginLeft: '12px', color: '#888' }}>
                      Est. cost per request: {estimateThinkingCost(thinkingBudget)}
                    </span>
                  </div>
                </div>
              )}

              {/* OpenAI: Reasoning Effort */}
              {currentProvider === 'openai' && (
                <div className="settings-item">
                  <label>
                    Reasoning Effort
                    <span className="info-icon" data-tooltip="Controls how much computational effort the model uses for reasoning">ℹ</span>
                  </label>
                  <select
                    value={reasoningEffort}
                    onChange={(e) => handleThinkingConfigChange({ effort: e.target.value })}
                    className="thinking-select"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
              )}
            </>
          )}
        </>
      )}

        {/* Apply Button */}
        <div className="settings-item apply-button-container">
          <button
            onClick={handleApplyProvider}
            className="apply-button"
            disabled={!currentModel}
          >
            Save Configuration
          </button>
        </div>
      </div>
    );
  }

  // Render API Keys management
  if (mode === "api_keys") {
    return (
      <div className="api-keys-container">
        <h3>API Key Management</h3>
        <p className="api-keys-description">
          Manage your API keys for different providers. API keys are stored securely and required
          for providers like OpenAI, Anthropic, Google, and OpenRouter. Ollama runs locally and
          doesn't require an API key.
        </p>

        {error && <div className="error-message">{error}</div>}
        {successMessage && <div className="success-message">{successMessage}</div>}

        {/* List all providers with API key inputs */}
        {availableProviders.map((provider) => {
          const needsApiKey = requiresApiKey(provider);
          const keySet = hasApiKey(provider);

          return (
            <div key={provider} className="api-key-item">
              <h4>
                {PROVIDER_DISPLAY_NAMES[provider] || provider}
                <span className={`key-status-badge ${!needsApiKey ? 'not-required' : keySet ? 'set' : 'not-set'}`}>
                  {!needsApiKey ? 'No API key needed' : keySet ? 'API Key Set' : 'Not Set'}
                </span>
              </h4>

              {needsApiKey ? (
                <>
                  <div className="api-key-input-group">
                    <input
                      type="password"
                      value={currentProvider === provider ? apiKeyInput : ''}
                      onChange={(e) => {
                        setCurrentProvider(provider);
                        handleApiKeyInputChange(provider, e.target.value);
                      }}
                      placeholder={`Enter ${PROVIDER_DISPLAY_NAMES[provider]} API key`}
                      className="api-key-input"
                    />
                    <button
                      onClick={() => {
                        setCurrentProvider(provider);
                        handleSetApiKey();
                      }}
                      className={`api-key-button ${keySet ? 'has-key' : ''}`}
                      disabled={currentProvider === provider && !apiKeyInput.trim()}
                    >
                      {keySet ? '✓ Update Key' : 'Set API Key'}
                    </button>
                    {keySet && (
                      <button
                        onClick={() => handleDeleteApiKey(provider)}
                        className="api-key-delete-button"
                        title="Delete API key"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                  {currentProvider === provider && apiKeyValidation && (
                    <div
                      className="api-key-validation"
                      style={{
                        marginTop: '8px',
                        fontSize: '13px',
                        color: apiKeyValidation.startsWith('✓') ? '#2e7d32' : '#e65100'
                      }}
                    >
                      {apiKeyValidation} • {apiKeyInput.length} characters
                    </div>
                  )}
                  {keySet && (
                    <div className="api-key-status">
                      Current key: {apiKeys[provider]}
                    </div>
                  )}
                </>
              ) : (
                <p style={{ color: '#666', fontSize: '14px', margin: '5px 0 0 0' }}>
                  This provider runs locally and doesn't require an API key.
                </p>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // Render Embedding Model settings
  return (
    <div className="provider-settings-container">
      {/* Embedding Configuration Section */}
      <div className="embedding-settings-section">
        <h3>Embedding Model</h3>

        {embeddingError && <div className="error-message">{embeddingError}</div>}
        {embeddingSuccessMessage && <div className="success-message">{embeddingSuccessMessage}</div>}

        {/* Embedding Provider Selection */}
        <div className="settings-item">
          <label>
            Provider
            <span className="info-icon" data-tooltip="Embeddings convert text to vectors for similarity search and document retrieval">ℹ</span>
          </label>
          <select
            value={currentEmbeddingProvider}
            onChange={(e) => handleEmbeddingProviderChange(e.target.value)}
            className="provider-select"
          >
            {embeddingProviders.map((provider) => (
              <option
                key={provider}
                value={provider}
                disabled={requiresApiKey(provider) && !hasApiKey(provider)}
              >
                {PROVIDER_DISPLAY_NAMES[provider] || provider}
                {requiresApiKey(provider) && !hasApiKey(provider) ? ' (API key required)' : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Note if using same provider without API key */}
        {requiresApiKey(currentEmbeddingProvider) && !hasApiKey(currentEmbeddingProvider) && (
          <div className="warning-message">
            ⚠️ {PROVIDER_DISPLAY_NAMES[currentEmbeddingProvider]} requires an API key.
            Please set it in the LLM configuration above.
          </div>
        )}

        {/* Embedding Model Selection */}
        <div className="settings-item">
          <label>
            Model
            <span className="info-icon" data-tooltip="Choose the specific embedding model to use">ℹ</span>
          </label>
          {embeddingModelLoading ? (
            <div className="skeleton skeleton-select"></div>
          ) : availableEmbeddingModels.length > 0 ? (
            <select
              value={currentEmbeddingModel || ""}
              onChange={(e) => handleEmbeddingModelChange(e.target.value)}
              className="model-select"
            >
              <option value="" disabled>
                Select an embedding model
              </option>
              {Object.entries(groupModels(currentEmbeddingProvider, availableEmbeddingModels, true)).map(([groupName, models]) => (
                <optgroup key={groupName} label={groupName}>
                  {models.map((model) => (
                    <option key={model} value={model}>
                      {model}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>
          ) : (
            <div className="no-models">
              {currentEmbeddingProvider === 'ollama' ? (
                <div>
                  <strong>No Ollama embedding models found.</strong>
                  <br />
                  Install embedding models using these commands:
                  <br />
                  <code style={{ display: 'block', marginTop: '8px', fontSize: '12px' }}>
                    ollama pull snowflake-arctic-embed2:latest<br />
                    ollama pull nomic-embed-text<br />
                    ollama pull mxbai-embed-large
                  </code>
                </div>
              ) : requiresApiKey(currentEmbeddingProvider) && !hasApiKey(currentEmbeddingProvider) ? (
                'Please set an API key first'
              ) : (
                'No embedding models available'
              )}
            </div>
          )}
        </div>

        {/* Apply Embedding Configuration Button */}
        <div className="settings-item apply-button-container">
          <button
            onClick={handleApplyEmbedding}
            className="apply-button"
            disabled={!currentEmbeddingModel}
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
}

// Type guards
function isProvidersResponse(obj: any): obj is ProvidersResponse {
  return typeof obj === "object" && Array.isArray(obj.providers);
}

function isProviderConfig(obj: any): obj is ProviderConfig {
  return (
    typeof obj === "object" &&
    typeof obj.provider === "string" &&
    (obj.model === null || typeof obj.model === "string") &&
    typeof obj.api_key_set === "boolean"
  );
}

function isModelsResponse(obj: any): obj is ModelsResponse {
  return (
    typeof obj === "object" &&
    Array.isArray(obj.models) &&
    typeof obj.success === "boolean"
  );
}

function isApiKeysStatusResponse(obj: any): obj is ApiKeysStatusResponse {
  return (
    typeof obj === "object" &&
    typeof obj.api_keys === "object" &&
    typeof obj.success === "boolean"
  );
}

function isEmbeddingConfig(obj: any): obj is EmbeddingConfig {
  return (
    typeof obj === "object" &&
    typeof obj.provider === "string" &&
    (obj.model === null || typeof obj.model === "string") &&
    typeof obj.success === "boolean"
  );
}

function isThinkingConfig(obj: any): obj is ThinkingConfig {
  return (
    typeof obj === "object" &&
    typeof obj.enabled === "boolean" &&
    typeof obj.budget_tokens === "number" &&
    typeof obj.effort === "string" &&
    typeof obj.summary === "string"
  );
}
