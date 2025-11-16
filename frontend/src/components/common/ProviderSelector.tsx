/**
 * Reusable Provider Selection Component
 */

import { PROVIDER_DISPLAY_NAMES } from "../../constants/providers";
import { requiresApiKey, hasApiKey } from "../../utils/validation";

interface ProviderSelectorProps {
  label: string;
  value: string;
  providers: string[];
  apiKeys: Record<string, string>;
  onChange: (provider: string) => void;
  tooltip?: string;
  disabled?: boolean;
}

export function ProviderSelector({
  label,
  value,
  providers,
  apiKeys,
  onChange,
  tooltip = "Select your provider",
  disabled = false
}: ProviderSelectorProps) {
  return (
    <div className="settings-item">
      <label>
        {label}
        <span className="info-icon" data-tooltip={tooltip}>ℹ</span>
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="provider-select"
        disabled={disabled}
      >
        {providers.map((provider) => {
          const needsKey = requiresApiKey(provider);
          const hasKey = hasApiKey(provider, apiKeys);
          const isDisabled = needsKey && !hasKey;

          return (
            <option
              key={provider}
              value={provider}
              disabled={isDisabled}
            >
              {PROVIDER_DISPLAY_NAMES[provider] || provider}
              {isDisabled ? ' (API key required)' : ''}
            </option>
          );
        })}
      </select>
    </div>
  );
}
