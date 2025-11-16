/**
 * Provider-related constants
 */

export const PROVIDER_DISPLAY_NAMES: Record<string, string> = {
  openai: "OpenAI",
  anthropic: "Anthropic",
  google: "Google (Gemini)",
  openrouter: "OpenRouter",
  ollama: "Ollama (Local)"
};

export const PROVIDERS_REQUIRING_API_KEY = [
  "openai",
  "anthropic",
  "google",
  "openrouter"
];
