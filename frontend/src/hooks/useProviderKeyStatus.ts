/**
 * Custom hook for checking provider API key status
 *
 * Centralizes the logic for determining whether a provider needs an API key
 * and whether one is currently set.
 */

import { requiresApiKey, hasApiKey } from '../utils/validation';

export interface ProviderKeyStatus {
  /** Whether this provider requires an API key */
  needsApiKey: boolean;
  /** Whether an API key is currently set for this provider */
  hasKey: boolean;
  /** The masked API key string, if available */
  maskedKey: string | undefined;
}

/**
 * Hook to check the API key status for a given provider
 *
 * @param provider - The provider name (e.g., 'openai', 'anthropic', 'ollama')
 * @param apiKeys - Record of provider names to masked API keys
 * @returns Provider key status information
 *
 * @example
 * ```tsx
 * const { needsApiKey, hasKey, maskedKey } = useProviderKeyStatus('openai', apiKeys);
 *
 * if (needsApiKey && !hasKey) {
 *   return <div>Please set your API key</div>;
 * }
 * ```
 */
export function useProviderKeyStatus(
  provider: string,
  apiKeys: Record<string, string>
): ProviderKeyStatus {
  return {
    needsApiKey: requiresApiKey(provider),
    hasKey: hasApiKey(provider, apiKeys),
    maskedKey: apiKeys[provider]
  };
}
