/**
 * LLM Provider Settings Component
 *
 * Handles language model provider and model selection.
 */

import { ProviderSelector, ModelSelector, ThinkingConfig } from "../common";
import { BUTTONS, TOOLTIPS } from "../../config";

interface LLMSettingsProps {
  // Configuration state
  currentProvider: string;
  currentModel: string | null;
  availableProviders: string[];

  // Model state
  models: string[];
  modelsLoading: boolean;

  // Thinking configuration
  supportsThinking: boolean;
  thinkingEnabled: boolean;
  thinkingBudgetTokens: number;
  thinkingEffort: string;

  // API keys
  apiKeys: Record<string, string>;

  // Messages
  error: string | null;
  successMessage: string | null;

  // Event handlers
  onProviderChange: (provider: string) => Promise<void>;
  onModelChange: (model: string) => Promise<void>;
  onUpdateThinkingConfig: (config: any) => Promise<void>;
  onApply: () => Promise<void>;
}

export function LLMSettings({
  currentProvider,
  currentModel,
  availableProviders,
  models,
  modelsLoading,
  supportsThinking,
  thinkingEnabled,
  thinkingBudgetTokens,
  thinkingEffort,
  apiKeys,
  error,
  successMessage,
  onProviderChange,
  onModelChange,
  onUpdateThinkingConfig,
  onApply
}: LLMSettingsProps) {
  return (
    <div className="provider-settings-container">
      <h3>Language Model</h3>

      {error && <div className="error-message">{error}</div>}
      {successMessage && <div className="success-message">{successMessage}</div>}

      <ProviderSelector
        label="Provider"
        value={currentProvider}
        providers={availableProviders}
        apiKeys={apiKeys}
        onChange={onProviderChange}
        tooltip={TOOLTIPS.LLM_PROVIDER}
      />

      <ModelSelector
        label="Model"
        provider={currentProvider}
        models={models}
        selectedModel={currentModel}
        loading={modelsLoading}
        apiKeys={apiKeys}
        onChange={onModelChange}
        tooltip={TOOLTIPS.MODEL_SELECT}
      />

      {supportsThinking && (
        <ThinkingConfig
          provider={currentProvider}
          enabled={thinkingEnabled}
          budgetTokens={thinkingBudgetTokens}
          effort={thinkingEffort}
          onUpdate={onUpdateThinkingConfig}
        />
      )}

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
  );
}
