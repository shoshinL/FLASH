/**
 * Thinking/Reasoning Configuration Component
 */

import { estimateThinkingCost } from "../../utils/costEstimation";
import type { ThinkingConfig as ThinkingConfigType } from "../../types/provider";
import { THINKING, LABELS, TOOLTIPS } from "../../config";

interface ThinkingConfigProps {
  provider: string;
  enabled: boolean;
  budgetTokens: number;
  effort: string;
  onUpdate: (updates: Partial<ThinkingConfigType>) => void;
}

export function ThinkingConfig({
  provider,
  enabled,
  budgetTokens,
  effort,
  onUpdate
}: ThinkingConfigProps) {
  return (
    <>
      {/* Enable/Disable Toggle */}
      <div className="settings-item checkbox-item">
        <label>
          <input
            type="checkbox"
            checked={enabled}
            onChange={(e) => onUpdate({ enabled: e.target.checked })}
          />
          <span>Enable extended thinking/reasoning</span>
          <span className="info-icon" data-tooltip={TOOLTIPS.THINKING_ENABLED}>ℹ</span>
        </label>
      </div>

      {enabled && (
        <>
          {/* Claude: Budget Tokens */}
          {provider === 'anthropic' && (
            <div className="settings-item">
              <label>
                {LABELS.THINKING_BUDGET}
                <span className="info-icon" data-tooltip={TOOLTIPS.THINKING_BUDGET}>ℹ</span>
              </label>
              <input
                type="number"
                value={budgetTokens}
                onChange={(e) => onUpdate({ budget_tokens: Number(e.target.value) })}
                min={THINKING.MIN_BUDGET_TOKENS}
                max={THINKING.MAX_BUDGET_TOKENS}
                step={THINKING.BUDGET_STEP}
                className="thinking-input"
              />
              <div style={{ marginTop: '8px', fontSize: '13px', color: '#666' }}>
                <span className="input-unit">{budgetTokens} tokens</span>
                <span style={{ marginLeft: '12px', color: '#888' }}>
                  Est. cost per request: {estimateThinkingCost(budgetTokens)}
                </span>
              </div>
            </div>
          )}

          {/* OpenAI: Reasoning Effort */}
          {provider === 'openai' && (
            <div className="settings-item">
              <label>
                {LABELS.REASONING_EFFORT}
                <span className="info-icon" data-tooltip={TOOLTIPS.REASONING_EFFORT}>ℹ</span>
              </label>
              <select
                value={effort}
                onChange={(e) => onUpdate({ effort: e.target.value })}
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
  );
}
