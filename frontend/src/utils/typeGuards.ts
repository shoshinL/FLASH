/**
 * TypeScript type guard utilities
 */

import type {
  ProvidersResponse,
  ProviderConfig,
  ModelsResponse,
  ApiKeysStatusResponse,
  EmbeddingConfig,
  ThinkingConfig
} from '../types/provider';

export function isProvidersResponse(obj: unknown): obj is ProvidersResponse {
  return typeof obj === "object" && obj !== null && Array.isArray((obj as ProvidersResponse).providers);
}

export function isProviderConfig(obj: unknown): obj is ProviderConfig {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as ProviderConfig).provider === "string" &&
    ((obj as ProviderConfig).model === null || typeof (obj as ProviderConfig).model === "string") &&
    typeof (obj as ProviderConfig).api_key_set === "boolean"
  );
}

export function isModelsResponse(obj: unknown): obj is ModelsResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    Array.isArray((obj as ModelsResponse).models) &&
    typeof (obj as ModelsResponse).success === "boolean"
  );
}

export function isApiKeysStatusResponse(obj: unknown): obj is ApiKeysStatusResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as ApiKeysStatusResponse).api_keys === "object" &&
    typeof (obj as ApiKeysStatusResponse).success === "boolean"
  );
}

export function isEmbeddingConfig(obj: unknown): obj is EmbeddingConfig {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as EmbeddingConfig).provider === "string" &&
    ((obj as EmbeddingConfig).model === null || typeof (obj as EmbeddingConfig).model === "string") &&
    typeof (obj as EmbeddingConfig).success === "boolean"
  );
}

export function isThinkingConfig(obj: unknown): obj is ThinkingConfig {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as ThinkingConfig).enabled === "boolean" &&
    typeof (obj as ThinkingConfig).budget_tokens === "number" &&
    typeof (obj as ThinkingConfig).effort === "string" &&
    typeof (obj as ThinkingConfig).summary === "string"
  );
}
