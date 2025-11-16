/**
 * Reusable Model Selection Component with Grouping
 */

import { groupModels } from "../../utils/modelGrouping";
import { requiresApiKey, hasApiKey } from "../../utils/validation";
import { PROVIDER_DISPLAY_NAMES } from "../../constants/providers";

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
  tooltip = "Choose the specific model to use"
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
              <strong>No Ollama {modelType} found.</strong>
              <br />
              Install {modelType} using these commands:
              <br />
              <code style={{ display: 'block', marginTop: '8px', fontSize: '12px' }}>
                {isEmbedding ? (
                  <>
                    ollama pull snowflake-arctic-embed2:latest<br />
                    ollama pull nomic-embed-text<br />
                    ollama pull mxbai-embed-large
                  </>
                ) : (
                  <>
                    ollama pull llama3.2<br />
                    ollama pull deepseek-r1:1.5b<br />
                    ollama pull qwen2.5:7b
                  </>
                )}
              </code>
            </div>
          ) : needsKey && !hasKey ? (
            `Please set an API key for ${providerName} first`
          ) : (
            `No ${modelType} available`
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
          Select a model
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
