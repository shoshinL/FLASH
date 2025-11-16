/**
 * Shared TypeScript types for provider configuration
 */

export interface ProviderConfig {
  provider: string;
  model: string | null;
  api_key_set: boolean;
}

export interface EmbeddingConfig {
  provider: string;
  model: string | null;
  api_key_set: boolean;
  success: boolean;
}

export interface ThinkingConfig {
  enabled: boolean;
  budget_tokens: number;
  effort: string;
  summary: string;
}

export interface ProvidersResponse {
  providers: string[];
  success?: boolean;
}

export interface ModelsResponse {
  models: string[];
  success: boolean;
  error?: string;
}

export interface ApiKeysStatusResponse {
  api_keys: Record<string, string>;
  success: boolean;
}

export interface ApiResponse {
  success: boolean;
  error?: string;
}

export type ProviderMode = "llm" | "embedding" | "api_keys";

export type ProviderName = "openai" | "anthropic" | "google" | "openrouter" | "ollama";
