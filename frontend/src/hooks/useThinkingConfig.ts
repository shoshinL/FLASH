/**
 * Custom hook for managing thinking/reasoning configuration
 */

import { useState, useEffect } from 'react';
import type { ThinkingConfig } from '../types/provider';
import { isThinkingConfig } from '../utils/typeGuards';
import { THINKING, ERRORS } from '../config';

export function useThinkingConfig() {
  const [enabled, setEnabled] = useState<boolean>(false);
  const [budgetTokens, setBudgetTokens] = useState<number>(THINKING.DEFAULT_BUDGET_TOKENS);
  const [effort, setEffort] = useState<string>(THINKING.DEFAULT_EFFORT);
  const [summary, setSummary] = useState<string>(THINKING.DEFAULT_SUMMARY);
  const [supportsThinking, setSupportsThinking] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchThinkingConfig();
  }, []);

  const fetchThinkingConfig = async () => {
    try {
      const response: unknown = await window.pywebview.api.get_thinking_config();
      if (isThinkingConfig(response)) {
        setEnabled(response.enabled);
        setBudgetTokens(response.budget_tokens);
        setEffort(response.effort);
        setSummary(response.summary);
      }
    } catch (err) {
      console.error("Error fetching thinking config:", err);
    }
  };

  const checkThinkingSupport = async (provider: string, model: string | null) => {
    try {
      const response: unknown = await window.pywebview.api.check_thinking_support(provider, model);
      if (typeof response === "object" && response !== null && "supports_thinking" in response) {
        setSupportsThinking(Boolean(response.supports_thinking));
      }
    } catch (err) {
      console.error("Error checking thinking support:", err);
      setSupportsThinking(false);
    }
  };

  const updateThinkingConfig = async (updates: Partial<ThinkingConfig>) => {
    const newConfig: ThinkingConfig = {
      enabled,
      budget_tokens: budgetTokens,
      effort,
      summary,
      ...updates
    };

    // Update local state
    if ('enabled' in updates) setEnabled(updates.enabled!);
    if ('budget_tokens' in updates) setBudgetTokens(updates.budget_tokens!);
    if ('effort' in updates) setEffort(updates.effort!);
    if ('summary' in updates) setSummary(updates.summary!);

    // Save to backend
    try {
      await window.pywebview.api.set_thinking_config(newConfig);
      // Silently save without showing success message
    } catch (err) {
      console.error("Error saving thinking config:", err);
      setError(ERRORS.THINKING_CONFIG_SAVE);
    }
  };

  return {
    enabled,
    budgetTokens,
    effort,
    summary,
    supportsThinking,
    error,
    setError,
    checkThinkingSupport,
    updateThinkingConfig,
    fetchThinkingConfig
  };
}
