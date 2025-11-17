/**
 * Embedding Settings Component
 *
 * Handles embedding provider and model selection.
 */

import { ProviderSelector, ModelSelector } from "../common";
import { PROVIDER_DISPLAY_NAMES } from "../../config/providers";
import { BUTTONS, TOOLTIPS, INFO } from "../../config";
import { useProviderKeyStatus } from "../../hooks";

interface EmbeddingSettingsProps {
  // Configuration state
  currentProvider: string;
  currentModel: string | null;
  embeddingProviders: string[];

  // Model state
  models: string[];
  modelsLoading: boolean;

  // API keys
  apiKeys: Record<string, string>;

  // Messages
  error: string | null;
  successMessage: string | null;

  // Event handlers
  onProviderChange: (provider: string) => Promise<void>;
  onModelChange: (model: string) => Promise<void>;
  onApply: () => Promise<void>;
}

export function EmbeddingSettings({
  currentProvider,
  currentModel,
  embeddingProviders,
  models,
  modelsLoading,
  apiKeys,
  error,
  successMessage,
  onProviderChange,
  onModelChange,
  onApply
}: EmbeddingSettingsProps) {
  const embeddingKeyStatus = useProviderKeyStatus(currentProvider, apiKeys);

  return (
    <div className="provider-settings-container">
      <div className="embedding-settings-section">
        <h3>Embedding Model</h3>

        {error && <div className="error-message">{error}</div>}
        {successMessage && <div className="success-message">{successMessage}</div>}

        <ProviderSelector
          label="Provider"
          value={currentProvider}
          providers={embeddingProviders}
          apiKeys={apiKeys}
          onChange={onProviderChange}
          tooltip={TOOLTIPS.EMBEDDING_PROVIDER}
        />

        {embeddingKeyStatus.needsApiKey && !embeddingKeyStatus.hasKey && (
          <div className="warning-message">
            {INFO.API_KEY_REQUIRED_TAB(PROVIDER_DISPLAY_NAMES[currentProvider])}
          </div>
        )}

        <ModelSelector
          label="Model"
          provider={currentProvider}
          models={models}
          selectedModel={currentModel}
          loading={modelsLoading}
          isEmbedding={true}
          apiKeys={apiKeys}
          onChange={onModelChange}
          tooltip={TOOLTIPS.EMBEDDING_MODEL_SELECT}
        />

        <div className="settings-item apply-button-container">
          <button
            onClick={onApply}
            className="apply-button"
            disabled={!currentModel}
          >
            {BUTTONS.SAVE_CONFIGURATION}
          </button>
        </div>
      </div>
    </div>
  );
}
