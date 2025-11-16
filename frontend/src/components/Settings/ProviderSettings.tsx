import { useState, useEffect } from "react";
import "./ProviderSettings.css";

// Import custom hooks
import { useProviderConfig, useApiKeys, useModels, useThinkingConfig } from "../../hooks";

// Import utilities
import {
  validateApiKey,
  requiresApiKey,
  hasApiKey,
  groupModels,
  estimateThinkingCost,
  isProvidersResponse,
  isEmbeddingConfig
} from "../../utils";

// Import constants
import { PROVIDER_DISPLAY_NAMES } from "../../constants/providers";

// Import types
import type { ProviderMode } from "../../types/provider";

interface ProviderSettingsProps {
  mode: ProviderMode;
}

export function ProviderSettings({ mode }: ProviderSettingsProps) {
  // === Custom Hooks ===
  const llmConfig = useProviderConfig();
  const apiKeysManager = useApiKeys();
  const llmModels = useModels();
  const thinkingConfig = useThinkingConfig();

  // === Local State ===
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);
  const [apiKeyInput, setApiKeyInput] = useState<string>("");
  const [apiKeyValidation, setApiKeyValidation] = useState<string | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<string>("openai");

  // Embedding-specific state
  const [embeddingProviders, setEmbeddingProviders] = useState<string[]>([]);
  const [currentEmbeddingProvider, setCurrentEmbeddingProvider] = useState<string>("openai");
  const [currentEmbeddingModel, setCurrentEmbeddingModel] = useState<string | null>(null);
  const embeddingModels = useModels();
  const [embeddingError, setEmbeddingError] = useState<string | null>(null);
  const [embeddingSuccessMessage, setEmbeddingSuccessMessage] = useState<string | null>(null);

  // === Effects ===
  useEffect(() => {
    fetchProviderData();
  }, []);

  useEffect(() => {
    if (llmConfig.currentProvider) {
      llmModels.fetchModels(llmConfig.currentProvider, false);
    }
  }, [llmConfig.currentProvider]);

  useEffect(() => {
    if (currentEmbeddingProvider) {
      embeddingModels.fetchModels(currentEmbeddingProvider, true);
    }
  }, [currentEmbeddingProvider]);

  useEffect(() => {
    if (llmConfig.currentProvider && llmConfig.currentModel) {
      thinkingConfig.checkThinkingSupport(llmConfig.currentProvider, llmConfig.currentModel);
    }
  }, [llmConfig.currentProvider, llmConfig.currentModel]);

  // === Data Fetching ===
  const fetchProviderData = async () => {
    try {
      // Fetch LLM providers
      const providersResp: unknown = await window.pywebview.api.get_available_providers();
      if (isProvidersResponse(providersResp)) {
        setAvailableProviders(providersResp.providers);
      }

      // Fetch embedding providers
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

      setEmbeddingError(null);
    } catch (err) {
      console.error("Error fetching provider data:", err);
      llmConfig.setError("Failed to load provider settings");
    }
  };

  // === Event Handlers ===
  const handleProviderChange = async (provider: string) => {
    llmConfig.setCurrentProvider(provider);
    llmConfig.setCurrentModel(null);
    setApiKeyInput("");
    llmConfig.setSuccessMessage(null);
    await llmModels.fetchModels(provider, false);
  };

  const handleModelChange = async (model: string) => {
    await llmConfig.updateProviderConfig(llmConfig.currentProvider, model);
  };

  const handleApiKeyInputChange = (provider: string, key: string) => {
    setApiKeyInput(key);
    const validation = validateApiKey(provider, key);
    setApiKeyValidation(validation);
  };

  const handleSetApiKey = async (provider: string) => {
    if (!apiKeyInput.trim()) {
      llmConfig.setError("Please enter an API key");
      return;
    }

    const success = await apiKeysManager.setApiKey(provider, apiKeyInput);
    if (success) {
      setApiKeyInput("");
      setApiKeyValidation(null);
      // Refresh models after setting API key
      if (provider === llmConfig.currentProvider) {
        await llmModels.fetchModels(provider, false);
      }
      if (provider === currentEmbeddingProvider) {
        await embeddingModels.fetchModels(provider, true);
      }
    }
  };

  const handleDeleteApiKey = async (provider: string) => {
    const success = await apiKeysManager.deleteApiKey(provider);
    if (success) {
      // Refresh models after deletion
      if (provider === llmConfig.currentProvider) {
        await llmModels.fetchModels(provider, false);
      }
      if (provider === currentEmbeddingProvider) {
        await embeddingModels.fetchModels(provider, true);
      }
    }
  };

  const handleEmbeddingProviderChange = async (provider: string) => {
    setCurrentEmbeddingProvider(provider);
    setCurrentEmbeddingModel(null);
    setEmbeddingSuccessMessage(null);
    await embeddingModels.fetchModels(provider, true);
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

  // === Loading State ===
  if (llmConfig.loading || apiKeysManager.loading) {
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

  // === Render LLM Configuration ===
  if (mode === "llm") {
    return (
      <div className="provider-settings-container">
        <h3>Language Model</h3>

        {llmConfig.error && <div className="error-message">{llmConfig.error}</div>}
        {llmConfig.successMessage && <div className="success-message">{llmConfig.successMessage}</div>}

        {/* Provider Selection */}
        <div className="settings-item">
          <label>
            Provider
            <span className="info-icon" data-tooltip="Select your LLM provider (OpenAI, Anthropic, Google, etc.)">ℹ</span>
          </label>
          <select
            value={llmConfig.currentProvider}
            onChange={(e) => handleProviderChange(e.target.value)}
            className="provider-select"
          >
            {availableProviders.map((provider) => (
              <option
                key={provider}
                value={provider}
                disabled={requiresApiKey(provider) && !hasApiKey(provider, apiKeysManager.apiKeys)}
              >
                {PROVIDER_DISPLAY_NAMES[provider] || provider}
                {requiresApiKey(provider) && !hasApiKey(provider, apiKeysManager.apiKeys) ? ' (API key required)' : ''}
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
          {llmModels.loading ? (
            <div className="skeleton skeleton-select"></div>
          ) : llmModels.models.length > 0 ? (
            <select
              value={llmConfig.currentModel || ""}
              onChange={(e) => handleModelChange(e.target.value)}
              className="model-select"
            >
              <option value="" disabled>
                Select a model
              </option>
              {Object.entries(groupModels(llmConfig.currentProvider, llmModels.models, false)).map(([groupName, models]) => (
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
              {llmConfig.currentProvider === 'ollama' ? (
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
              ) : requiresApiKey(llmConfig.currentProvider) && !hasApiKey(llmConfig.currentProvider, apiKeysManager.apiKeys) ? (
                'Please set an API key first'
              ) : (
                'No models available'
              )}
            </div>
          )}
        </div>

        {/* Thinking/Reasoning Configuration */}
        {thinkingConfig.supportsThinking && (
          <>
            <div className="settings-item checkbox-item">
              <label>
                <input
                  type="checkbox"
                  checked={thinkingConfig.enabled}
                  onChange={(e) => thinkingConfig.updateThinkingConfig({ enabled: e.target.checked })}
                />
                <span>Enable extended thinking/reasoning</span>
                <span className="info-icon" data-tooltip="Allow the model to spend more time reasoning before responding - improves quality but increases cost">ℹ</span>
              </label>
            </div>

            {thinkingConfig.enabled && (
              <>
                {/* Claude: Budget Tokens */}
                {llmConfig.currentProvider === 'anthropic' && (
                  <div className="settings-item">
                    <label>
                      Thinking Budget
                      <span className="info-icon" data-tooltip="Number of tokens allocated for thinking - higher values allow deeper reasoning but cost more">ℹ</span>
                    </label>
                    <input
                      type="number"
                      value={thinkingConfig.budgetTokens}
                      onChange={(e) => thinkingConfig.updateThinkingConfig({ budget_tokens: Number(e.target.value) })}
                      min={500}
                      max={10000}
                      step={500}
                      className="thinking-input"
                    />
                    <div style={{ marginTop: '8px', fontSize: '13px', color: '#666' }}>
                      <span className="input-unit">{thinkingConfig.budgetTokens} tokens</span>
                      <span style={{ marginLeft: '12px', color: '#888' }}>
                        Est. cost per request: {estimateThinkingCost(thinkingConfig.budgetTokens)}
                      </span>
                    </div>
                  </div>
                )}

                {/* OpenAI: Reasoning Effort */}
                {llmConfig.currentProvider === 'openai' && (
                  <div className="settings-item">
                    <label>
                      Reasoning Effort
                      <span className="info-icon" data-tooltip="Controls how much computational effort the model uses for reasoning">ℹ</span>
                    </label>
                    <select
                      value={thinkingConfig.effort}
                      onChange={(e) => thinkingConfig.updateThinkingConfig({ effort: e.target.value })}
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
            onClick={() => llmConfig.updateProviderConfig(llmConfig.currentProvider, llmConfig.currentModel)}
            className="apply-button"
            disabled={!llmConfig.currentModel}
          >
            Save Configuration
          </button>
        </div>
      </div>
    );
  }

  // === Render API Keys Management ===
  if (mode === "api_keys") {
    return (
      <div className="api-keys-container">
        <h3>API Key Management</h3>
        <p className="api-keys-description">
          Manage your API keys for different providers. API keys are stored securely and required
          for providers like OpenAI, Anthropic, Google, and OpenRouter. Ollama runs locally and
          doesn't require an API key.
        </p>

        {apiKeysManager.error && <div className="error-message">{apiKeysManager.error}</div>}
        {apiKeysManager.successMessage && <div className="success-message">{apiKeysManager.successMessage}</div>}

        {availableProviders.map((provider) => {
          const needsApiKey = requiresApiKey(provider);
          const keySet = hasApiKey(provider, apiKeysManager.apiKeys);

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
                      value={selectedProvider === provider ? apiKeyInput : ''}
                      onChange={(e) => {
                        setSelectedProvider(provider);
                        handleApiKeyInputChange(provider, e.target.value);
                      }}
                      placeholder={`Enter ${PROVIDER_DISPLAY_NAMES[provider]} API key`}
                      className="api-key-input"
                    />
                    <button
                      onClick={() => {
                        setSelectedProvider(provider);
                        handleSetApiKey(provider);
                      }}
                      className={`api-key-button ${keySet ? 'has-key' : ''}`}
                      disabled={selectedProvider === provider && !apiKeyInput.trim()}
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
                  {selectedProvider === provider && apiKeyValidation && (
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
                      Current key: {apiKeysManager.apiKeys[provider]}
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

  // === Render Embedding Model Settings ===
  return (
    <div className="provider-settings-container">
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
                disabled={requiresApiKey(provider) && !hasApiKey(provider, apiKeysManager.apiKeys)}
              >
                {PROVIDER_DISPLAY_NAMES[provider] || provider}
                {requiresApiKey(provider) && !hasApiKey(provider, apiKeysManager.apiKeys) ? ' (API key required)' : ''}
              </option>
            ))}
          </select>
        </div>

        {/* Warning if API key required */}
        {requiresApiKey(currentEmbeddingProvider) && !hasApiKey(currentEmbeddingProvider, apiKeysManager.apiKeys) && (
          <div className="warning-message">
            ⚠️ {PROVIDER_DISPLAY_NAMES[currentEmbeddingProvider]} requires an API key.
            Please set it in the API Keys tab.
          </div>
        )}

        {/* Embedding Model Selection */}
        <div className="settings-item">
          <label>
            Model
            <span className="info-icon" data-tooltip="Choose the specific embedding model to use">ℹ</span>
          </label>
          {embeddingModels.loading ? (
            <div className="skeleton skeleton-select"></div>
          ) : embeddingModels.models.length > 0 ? (
            <select
              value={currentEmbeddingModel || ""}
              onChange={(e) => handleEmbeddingModelChange(e.target.value)}
              className="model-select"
            >
              <option value="" disabled>
                Select an embedding model
              </option>
              {Object.entries(groupModels(currentEmbeddingProvider, embeddingModels.models, true)).map(([groupName, models]) => (
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
              ) : requiresApiKey(currentEmbeddingProvider) && !hasApiKey(currentEmbeddingProvider, apiKeysManager.apiKeys) ? (
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
