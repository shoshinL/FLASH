/**
 * API Key Management Component
 *
 * Handles API key configuration for all providers.
 */

import { APIKeyInput } from "../common";
import { PROVIDER_DISPLAY_NAMES } from "../../config/providers";
import { requiresApiKey, hasApiKey } from "../../utils/validation";

interface APIKeySettingsProps {
  // Available providers
  availableProviders: string[];

  // API keys
  apiKeys: Record<string, string>;

  // Messages
  error: string | null;
  successMessage: string | null;

  // Event handlers
  onSetApiKey: (provider: string, key: string) => Promise<boolean>;
  onDeleteApiKey: (provider: string) => Promise<boolean>;
}

export function APIKeySettings({
  availableProviders,
  apiKeys,
  error,
  successMessage,
  onSetApiKey,
  onDeleteApiKey
}: APIKeySettingsProps) {
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

      {availableProviders.map((provider) => {
        const needsApiKey = requiresApiKey(provider);
        const keySet = hasApiKey(provider, apiKeys);
        const maskedKey = apiKeys[provider];

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
                maskedKey={maskedKey}
                onSet={(key) => onSetApiKey(provider, key)}
                onDelete={() => onDeleteApiKey(provider)}
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
