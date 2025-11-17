/**
 * Reusable Model Selection Component with Grouping
 */

import { groupModels } from "../../utils/modelGrouping";
import { requiresApiKey, hasApiKey } from "../../utils/validation";
import { PROVIDER_DISPLAY_NAMES } from "../../config/providers";
import { INFO, OLLAMA_EXAMPLES } from "../../config";

interface ModelSelectorProps {
  label: string;
  provider: string;
  models: string[];
  selectedModel: string | null;
  loading: boolean;
  isEmbedding?: boolean;
  apiKeys: Record<string, string>;
  onChange: (model: string) => void;
  tooltip?: string;
}

export function ModelSelector({
  label,
  provider,
  models,
  selectedModel,
  loading,
  isEmbedding = false,
  apiKeys,
  onChange,
  tooltip
}: ModelSelectorProps) {
  const needsKey = requiresApiKey(provider);
  const hasKey = hasApiKey(provider, apiKeys);

  if (loading) {
    return (
      <div className="settings-item">
        <label>
          {label}
          <span className="info-icon" data-tooltip={tooltip}>ℹ</span>
        </label>
        <div className="skeleton skeleton-select"></div>
      </div>
    );
  }

  if (models.length === 0) {
    const modelType = isEmbedding ? 'embedding models' : 'models';
    const providerName = PROVIDER_DISPLAY_NAMES[provider] || provider;

    return (
      <div className="settings-item">
        <label>
          {label}
          <span className="info-icon" data-tooltip={tooltip}>ℹ</span>
        </label>
        <div className="no-models">
          {provider === 'ollama' ? (
            <div>
              <strong>{INFO.OLLAMA_NO_MODELS_TITLE(isEmbedding)}</strong>
              <br />
              {INFO.OLLAMA_INSTALL_PROMPT(isEmbedding)}
              <br />
              <code style={{ display: 'block', marginTop: '8px', fontSize: '12px' }}>
                {(isEmbedding ? OLLAMA_EXAMPLES.EMBEDDING_MODELS : OLLAMA_EXAMPLES.LLM_MODELS).map((model, idx) => (
                  <span key={model}>
                    {OLLAMA_EXAMPLES.INSTALL_COMMAND} {model}
                    {idx < (isEmbedding ? OLLAMA_EXAMPLES.EMBEDDING_MODELS : OLLAMA_EXAMPLES.LLM_MODELS).length - 1 && <br />}
                  </span>
                ))}
              </code>
            </div>
          ) : needsKey && !hasKey ? (
            INFO.API_KEY_REQUIRED(providerName)
          ) : (
            INFO.NO_MODELS_AVAILABLE(modelType)
          )}
        </div>
      </div>
    );
  }

  const groupedModels = groupModels(provider, models, isEmbedding);

  return (
    <div className="settings-item">
      <label>
        {label}
        <span className="info-icon" data-tooltip={tooltip}>ℹ</span>
      </label>
      <select
        value={selectedModel || ""}
        onChange={(e) => onChange(e.target.value)}
        className="model-select"
      >
        <option value="" disabled>
          {INFO.SELECT_MODEL}
        </option>
        {Object.entries(groupedModels).map(([groupName, groupModels]) => (
          <optgroup key={groupName} label={groupName}>
            {groupModels.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </optgroup>
        ))}
      </select>
    </div>
  );
}
