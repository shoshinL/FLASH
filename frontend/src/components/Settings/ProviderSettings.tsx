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

interface ProviderSettingsProps {
  mode: "llm" | "embedding";
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
            setError("Ollama is not running or no models are installed. Please start Ollama and pull models.");
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
            setEmbeddingError("Ollama is not running or no embedding models are installed. Please start Ollama and pull embedding models (e.g., 'ollama pull snowflake-arctic-embed2:latest').");
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
      setSuccessMessage("Thinking configuration updated!");
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error("Error saving thinking config:", err);
      setError("Failed to save thinking configuration");
    }
  };

  if (loading) {
    return <div className="provider-settings-loading">Loading provider settings...</div>;
  }

  // Render LLM Provider settings
  if (mode === "llm") {
    return (
      <div className="provider-settings-container">
        <h3>LLM Provider Configuration</h3>

        {error && <div className="error-message">{error}</div>}
        {successMessage && <div className="success-message">{successMessage}</div>}

      {/* Provider Selection */}
      <div className="settings-item">
        <label>Model Provider:</label>
        <select
          value={currentProvider}
          onChange={(e) => handleProviderChange(e.target.value)}
          className="provider-select"
        >
          {availableProviders.map((provider) => (
            <option key={provider} value={provider}>
              {PROVIDER_DISPLAY_NAMES[provider] || provider}
            </option>
          ))}
        </select>
      </div>

      {/* API Key Input (only for providers that need it) */}
      {requiresApiKey(currentProvider) && (
        <div className="settings-item api-key-section">
          <label>
            {PROVIDER_DISPLAY_NAMES[currentProvider]} API Key:
          </label>
          <div className="api-key-input-group">
            <input
              type="password"
              value={apiKeyInput}
              onChange={(e) => setApiKeyInput(e.target.value)}
              placeholder={`Enter ${PROVIDER_DISPLAY_NAMES[currentProvider]} API key`}
              className="api-key-input"
            />
            <button
              onClick={handleSetApiKey}
              className={`api-key-button ${hasApiKey(currentProvider) ? 'has-key' : ''}`}
            >
              {hasApiKey(currentProvider) ? '✓ Update Key' : 'Set API Key'}
            </button>
          </div>
          {hasApiKey(currentProvider) && (
            <div className="api-key-status">
              Current key: {apiKeys[currentProvider]}
            </div>
          )}
        </div>
      )}

      {/* Model Selection */}
      <div className="settings-item">
        <label>Model:</label>
        {modelLoading ? (
          <div className="model-loading">Loading models...</div>
        ) : availableModels.length > 0 ? (
          <select
            value={currentModel || ""}
            onChange={(e) => handleModelChange(e.target.value)}
            className="model-select"
          >
            <option value="" disabled>
              Select a model
            </option>
            {availableModels.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        ) : (
          <div className="no-models">
            {currentProvider === 'ollama'
              ? 'No Ollama models found. Please install models using "ollama pull <model-name>"'
              : requiresApiKey(currentProvider) && !hasApiKey(currentProvider)
              ? 'Please set an API key first'
              : 'No models available'}
          </div>
        )}
      </div>

      {/* Thinking/Reasoning Configuration */}
      {providerSupportsThinking && (
        <div className="thinking-config-section">
          <h4>Thinking/Reasoning Settings</h4>

          {/* Enable/Disable Toggle */}
          <div className="settings-item">
            <label>
              <input
                type="checkbox"
                checked={thinkingEnabled}
                onChange={(e) => handleThinkingConfigChange({ enabled: e.target.checked })}
              />
              Enable Extended Thinking/Reasoning
            </label>
            <p className="hint">
              Extended thinking allows the model to spend more time reasoning before responding
            </p>
          </div>

          {thinkingEnabled && (
            <>
              {/* Claude: Budget Tokens */}
              {currentProvider === 'anthropic' && (
                <div className="settings-item">
                  <label>Thinking Budget (tokens):</label>
                  <input
                    type="number"
                    value={thinkingBudget}
                    onChange={(e) => handleThinkingConfigChange({ budget_tokens: Number(e.target.value) })}
                    min={500}
                    max={10000}
                    step={500}
                    className="thinking-input"
                  />
                  <span className="hint">
                    More tokens = deeper thinking (costs more)
                  </span>
                </div>
              )}

              {/* OpenAI: Reasoning Effort */}
              {currentProvider === 'openai' && (
                <>
                  <div className="settings-item">
                    <label>Reasoning Effort:</label>
                    <select
                      value={reasoningEffort}
                      onChange={(e) => handleThinkingConfigChange({ effort: e.target.value })}
                      className="thinking-select"
                    >
                      <option value="low">Low (faster, cheaper)</option>
                      <option value="medium">Medium (balanced)</option>
                      <option value="high">High (slower, more thorough)</option>
                    </select>
                  </div>

                  <div className="settings-item">
                    <label>Reasoning Summary:</label>
                    <select
                      value={reasoningSummary}
                      onChange={(e) => handleThinkingConfigChange({ summary: e.target.value })}
                      className="thinking-select"
                    >
                      <option value="auto">Auto</option>
                      <option value="concise">Concise</option>
                      <option value="detailed">Detailed</option>
                    </select>
                  </div>
                </>
              )}

              {/* Google/Ollama: Info only */}
              {(currentProvider === 'google' || currentProvider === 'ollama') && (
                <div className="settings-item">
                  <p className="hint">
                    {currentProvider === 'google'
                      ? 'Thinking mode is enabled for this model'
                      : 'This model supports native thinking mode'}
                  </p>
                </div>
              )}
            </>
          )}
        </div>
      )}

        {/* Apply Button */}
        <div className="settings-item">
          <button
            onClick={handleApplyProvider}
            className="apply-button"
            disabled={!currentModel}
          >
            Apply LLM Configuration
          </button>
        </div>
      </div>
    );
  }

  // Render Embedding Provider settings
  return (
    <div className="provider-settings-container">
      {/* Embedding Configuration Section */}
      <div className="embedding-settings-section">
        <h3>Embedding Model Configuration</h3>
        <p className="section-description">
          Embeddings are used to convert text into numerical vectors for similarity search and retrieval.
          You can use a different provider for embeddings than your LLM provider.
        </p>

        {embeddingError && <div className="error-message">{embeddingError}</div>}
        {embeddingSuccessMessage && <div className="success-message">{embeddingSuccessMessage}</div>}

        {/* Embedding Provider Selection */}
        <div className="settings-item">
          <label>Embedding Provider:</label>
          <select
            value={currentEmbeddingProvider}
            onChange={(e) => handleEmbeddingProviderChange(e.target.value)}
            className="provider-select"
          >
            {embeddingProviders.map((provider) => (
              <option key={provider} value={provider}>
                {PROVIDER_DISPLAY_NAMES[provider] || provider}
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
          <label>Embedding Model:</label>
          {embeddingModelLoading ? (
            <div className="model-loading">Loading embedding models...</div>
          ) : availableEmbeddingModels.length > 0 ? (
            <select
              value={currentEmbeddingModel || ""}
              onChange={(e) => handleEmbeddingModelChange(e.target.value)}
              className="model-select"
            >
              <option value="" disabled>
                Select an embedding model
              </option>
              {availableEmbeddingModels.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          ) : (
            <div className="no-models">
              {currentEmbeddingProvider === 'ollama'
                ? 'No Ollama embedding models found. Please install models using "ollama pull snowflake-arctic-embed2:latest"'
                : requiresApiKey(currentEmbeddingProvider) && !hasApiKey(currentEmbeddingProvider)
                ? 'Please set an API key first'
                : 'No embedding models available'}
            </div>
          )}
        </div>

        {/* Apply Embedding Configuration Button */}
        <div className="settings-item">
          <button
            onClick={handleApplyEmbedding}
            className="apply-button"
            disabled={!currentEmbeddingModel}
          >
            Apply Embedding Configuration
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
