/**
 * Reusable API Key Input Component with Validation
 */

import { useState } from "react";
import { validateApiKey } from "../../utils/validation";
import { PROVIDER_DISPLAY_NAMES } from "../../config/providers";
import { BUTTONS } from "../../config";

interface APIKeyInputProps {
  provider: string;
  hasKey: boolean;
  maskedKey?: string;
  onSet: (key: string) => Promise<boolean>;
  onDelete?: () => Promise<boolean>;
  showStatus?: boolean;
}

export function APIKeyInput({
  provider,
  hasKey,
  maskedKey,
  onSet,
  onDelete,
  showStatus = true
}: APIKeyInputProps) {
  const [keyInput, setKeyInput] = useState("");
  const [validation, setValidation] = useState<string | null>(null);

  const providerName = PROVIDER_DISPLAY_NAMES[provider] || provider;

  const handleInputChange = (value: string) => {
    setKeyInput(value);
    const validationResult = validateApiKey(provider, value);
    setValidation(validationResult);
  };

  const handleSetKey = async () => {
    if (!keyInput.trim()) return;

    const success = await onSet(keyInput);
    if (success) {
      setKeyInput("");
      setValidation(null);
    }
  };

  const handleDeleteKey = async () => {
    if (onDelete) {
      await onDelete();
    }
  };

  return (
    <div className="api-key-input-group-wrapper">
      <div className="api-key-input-group">
        <input
          type="password"
          value={keyInput}
          onChange={(e) => handleInputChange(e.target.value)}
          placeholder={`Enter ${providerName} API key`}
          className="api-key-input"
        />
        <button
          onClick={handleSetKey}
          className={`api-key-button ${hasKey ? 'has-key' : ''}`}
          disabled={!keyInput.trim()}
        >
          {hasKey ? BUTTONS.UPDATE_API_KEY : BUTTONS.SET_API_KEY}
        </button>
        {hasKey && onDelete && (
          <button
            onClick={handleDeleteKey}
            className="api-key-delete-button"
            title={BUTTONS.DELETE_API_KEY_TITLE}
          >
            🗑️
          </button>
        )}
      </div>

      {validation && (
        <div
          className="api-key-validation"
          style={{
            marginTop: '8px',
            fontSize: '13px',
            color: validation.startsWith('✓') ? '#2e7d32' : '#e65100'
          }}
        >
          {validation} • {keyInput.length} characters
        </div>
      )}

      {showStatus && hasKey && maskedKey && (
        <div className="api-key-status">
          Current key: {maskedKey}
        </div>
      )}
    </div>
  );
}
