import { useState, useEffect } from "react";
import "./ProviderSettings.css";

interface ProviderConfig {
  provider: string;
  model: string | null;
  api_key_set: boolean;
}

interface ProvidersResponse {
  providers: string[];
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

export function ProviderSettings() {
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

  useEffect(() => {
    fetchProviderData();
  }, []);

  useEffect(() => {
    if (currentProvider) {
      fetchAvailableModels(currentProvider);
    }
  }, [currentProvider]);

  const fetchProviderData = async () => {
    setLoading(true);
    try {
      // Fetch available providers
      const providersResp: unknown = await window.pywebview.api.get_available_providers();
      if (isProvidersResponse(providersResp)) {
        setAvailableProviders(providersResp.providers);
      }

      // Fetch current provider config
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

      setError(null);
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

  const requiresApiKey = (provider: string): boolean => {
    return provider !== "ollama";
  };

  const hasApiKey = (provider: string): boolean => {
    return !!apiKeys[provider];
  };

  if (loading) {
    return <div className="provider-settings-loading">Loading provider settings...</div>;
  }

  return (
    <div className="provider-settings-container">
      <h3>Model Provider Configuration</h3>

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

      {/* Apply Button */}
      <div className="settings-item">
        <button
          onClick={handleApplyProvider}
          className="apply-button"
          disabled={!currentModel}
        >
          Apply Provider Configuration
        </button>
      </div>

      {/* Provider Info */}
      <div className="provider-info">
        <h4>About this provider:</h4>
        <div className="provider-description">
          {getProviderDescription(currentProvider)}
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

function getProviderDescription(provider: string): string {
  const descriptions: Record<string, string> = {
    openai: "OpenAI provides GPT models including o1, o3-mini (reasoning models), and GPT-4o for general tasks. Requires an OpenAI API key.",
    anthropic: "Anthropic provides Claude models, known for being helpful, harmless, and honest. Supports long context windows. Requires an Anthropic API key.",
    google: "Google provides Gemini models with multimodal capabilities. Includes thinking models like Gemini 2.0 Flash Thinking. Requires a Google AI API key.",
    openrouter: "OpenRouter provides access to multiple AI models through a single API. Great for trying different models. Requires an OpenRouter API key.",
    ollama: "Ollama runs LLM models locally on your machine. No API key required. Install models using 'ollama pull <model-name>' in your terminal."
  };
  return descriptions[provider] || "No description available.";
}
