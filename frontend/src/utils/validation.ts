/**
 * Validation utilities for API keys and other inputs
 */

export function validateApiKey(provider: string, key: string): string | null {
  if (!key.trim()) {
    return null;
  }

  const trimmedKey = key.trim();

  switch (provider) {
    case 'openai':
      if (!trimmedKey.startsWith('sk-')) {
        return '⚠️ OpenAI keys should start with "sk-"';
      }
      if (trimmedKey.length < 40) {
        return '⚠️ OpenAI keys are typically longer';
      }
      return '✓ Valid format';

    case 'anthropic':
      if (!trimmedKey.startsWith('sk-ant-')) {
        return '⚠️ Anthropic keys should start with "sk-ant-"';
      }
      if (trimmedKey.length < 40) {
        return '⚠️ Anthropic keys are typically longer';
      }
      return '✓ Valid format';

    case 'google':
      if (trimmedKey.length < 30) {
        return '⚠️ Google API keys are typically longer';
      }
      return '✓ Valid format';

    case 'openrouter':
      if (!trimmedKey.startsWith('sk-or-')) {
        return '⚠️ OpenRouter keys should start with "sk-or-"';
      }
      if (trimmedKey.length < 40) {
        return '⚠️ OpenRouter keys are typically longer';
      }
      return '✓ Valid format';

    default:
      return trimmedKey.length > 20 ? '✓ Valid length' : '⚠️ Key seems too short';
  }
}

export function requiresApiKey(provider: string): boolean {
  return provider !== "ollama";
}

export function hasApiKey(provider: string, apiKeys: Record<string, string>): boolean {
  return !!apiKeys[provider];
}
