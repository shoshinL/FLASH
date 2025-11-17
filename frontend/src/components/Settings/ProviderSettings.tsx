import { useState, useEffect } from "react";
import "./ProviderSettings.css";

// Custom hooks
import { useProviderConfig, useApiKeys, useModels, useThinkingConfig } from "../../hooks";

// Reusable components
import {
  ProviderSelector,
  ModelSelector,
  APIKeyInput,
  ThinkingConfig,
  SettingsLoadingSkeleton
} from "../common";

// Utilities
import { requiresApiKey, hasApiKey, isProvidersResponse, isEmbeddingConfig } from "../../utils";

// Constants
import { PROVIDER_DISPLAY_NAMES } from "../../config/providers";
import { ERRORS, SUCCESS, INFO, BUTTONS, TOOLTIPS } from "../../config";

// Types
import type { ProviderMode } from "../../types/provider";

interface ProviderSettingsProps {
  mode: ProviderMode;
}

export function ProviderSettings({ mode }: ProviderSettingsProps) {
  // === Hooks ===
  const llmConfig = useProviderConfig();
  const apiKeysManager = useApiKeys();
  const llmModels = useModels();
  const thinkingConfig = useThinkingConfig();

  // === Local State ===
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);

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
      const providersResp: unknown = await window.pywebview.api.get_available_providers();
      if (isProvidersResponse(providersResp)) {
        setAvailableProviders(providersResp.providers);
      }

      const embeddingProvidersResp: unknown = await window.pywebview.api.get_embedding_providers();
      if (isProvidersResponse(embeddingProvidersResp)) {
        setEmbeddingProviders(embeddingProvidersResp.providers);
      }

      const embeddingConfigResp: unknown = await window.pywebview.api.get_embedding_config();
      if (isEmbeddingConfig(embeddingConfigResp)) {
        setCurrentEmbeddingProvider(embeddingConfigResp.provider);
        setCurrentEmbeddingModel(embeddingConfigResp.model);
      }

      setEmbeddingError(null);
    } catch (err) {
      console.error("Error fetching provider data:", err);
      llmConfig.setError(ERRORS.PROVIDER_SETTINGS_LOAD);
    }
  };

  // === Event Handlers ===
  const handleProviderChange = async (provider: string) => {
    llmConfig.setCurrentProvider(provider);
    llmConfig.setCurrentModel(null);
    llmConfig.setSuccessMessage(null);
    await llmModels.fetchModels(provider, false);
  };

  const handleModelChange = async (model: string) => {
    await llmConfig.updateProviderConfig(llmConfig.currentProvider, model);
  };

  const handleSetApiKey = async (provider: string, key: string) => {
    const success = await apiKeysManager.setApiKey(provider, key);
    if (success) {
      // Refresh models after setting API key
      if (provider === llmConfig.currentProvider) {
        await llmModels.fetchModels(provider, false);
      }
      if (provider === currentEmbeddingProvider) {
        await embeddingModels.fetchModels(provider, true);
      }
    }
    return success;
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
    return success;
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
        setEmbeddingSuccessMessage(SUCCESS.EMBEDDING_MODEL_UPDATED);
        setTimeout(() => setEmbeddingSuccessMessage(null), 3000);
      } else {
        setEmbeddingError(ERRORS.EMBEDDING_MODEL_SET);
      }
    } catch (err) {
      console.error("Error setting embedding model:", err);
      setEmbeddingError(ERRORS.EMBEDDING_MODEL_SET);
    }
  };

  const handleApplyEmbedding = async () => {
    try {
      const response: unknown = await window.pywebview.api.set_embedding_config(currentEmbeddingProvider, currentEmbeddingModel);
      if (typeof response === "object" && response !== null && "success" in response && response.success) {
        setEmbeddingSuccessMessage(SUCCESS.EMBEDDING_CONFIG_SAVED);
        setTimeout(() => setEmbeddingSuccessMessage(null), 3000);
        setEmbeddingError(null);
      } else {
        const errorMsg = (typeof response === "object" && response !== null && "error" in response)
          ? String(response.error)
          : ERRORS.EMBEDDING_CONFIG_SAVE;
        setEmbeddingError(errorMsg);
      }
    } catch (err) {
      console.error("Error applying embedding config:", err);
      setEmbeddingError(ERRORS.EMBEDDING_CONFIG_SAVE);
    }
  };

  // === Loading State ===
  if (llmConfig.loading || apiKeysManager.loading) {
    return <SettingsLoadingSkeleton />;
  }

  // === Render LLM Configuration ===
  if (mode === "llm") {
    return (
      <div className="provider-settings-container">
        <h3>Language Model</h3>

        {llmConfig.error && <div className="error-message">{llmConfig.error}</div>}
        {llmConfig.successMessage && <div className="success-message">{llmConfig.successMessage}</div>}

        <ProviderSelector
          label="Provider"
          value={llmConfig.currentProvider}
          providers={availableProviders}
          apiKeys={apiKeysManager.apiKeys}
          onChange={handleProviderChange}
          tooltip={TOOLTIPS.LLM_PROVIDER}
        />

        <ModelSelector
          label="Model"
          provider={llmConfig.currentProvider}
          models={llmModels.models}
          selectedModel={llmConfig.currentModel}
          loading={llmModels.loading}
          apiKeys={apiKeysManager.apiKeys}
          onChange={handleModelChange}
          tooltip={TOOLTIPS.MODEL_SELECT}
        />

        {thinkingConfig.supportsThinking && (
          <ThinkingConfig
            provider={llmConfig.currentProvider}
            enabled={thinkingConfig.enabled}
            budgetTokens={thinkingConfig.budgetTokens}
            effort={thinkingConfig.effort}
            onUpdate={thinkingConfig.updateThinkingConfig}
          />
        )}

        <div className="settings-item apply-button-container">
          <button
            onClick={() => llmConfig.updateProviderConfig(llmConfig.currentProvider, llmConfig.currentModel)}
            className="apply-button"
            disabled={!llmConfig.currentModel}
          >
            {BUTTONS.SAVE_CONFIGURATION}
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
                <APIKeyInput
                  provider={provider}
                  hasKey={keySet}
                  maskedKey={apiKeysManager.apiKeys[provider]}
                  onSet={(key) => handleSetApiKey(provider, key)}
                  onDelete={() => handleDeleteApiKey(provider)}
                  showStatus={true}
                />
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

        <ProviderSelector
          label="Provider"
          value={currentEmbeddingProvider}
          providers={embeddingProviders}
          apiKeys={apiKeysManager.apiKeys}
          onChange={handleEmbeddingProviderChange}
          tooltip={TOOLTIPS.EMBEDDING_PROVIDER}
        />

        {requiresApiKey(currentEmbeddingProvider) && !hasApiKey(currentEmbeddingProvider, apiKeysManager.apiKeys) && (
          <div className="warning-message">
            {INFO.API_KEY_REQUIRED_TAB(PROVIDER_DISPLAY_NAMES[currentEmbeddingProvider])}
          </div>
        )}

        <ModelSelector
          label="Model"
          provider={currentEmbeddingProvider}
          models={embeddingModels.models}
          selectedModel={currentEmbeddingModel}
          loading={embeddingModels.loading}
          isEmbedding={true}
          apiKeys={apiKeysManager.apiKeys}
          onChange={handleEmbeddingModelChange}
          tooltip={TOOLTIPS.EMBEDDING_MODEL_SELECT}
        />

        <div className="settings-item apply-button-container">
          <button
            onClick={handleApplyEmbedding}
            className="apply-button"
            disabled={!currentEmbeddingModel}
          >
            {BUTTONS.SAVE_CONFIGURATION}
          </button>
        </div>
      </div>
    </div>
  );
}
