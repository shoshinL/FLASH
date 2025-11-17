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

import type {
  Settings,
  ProfilesResponse,
  DecksResponse,
  AnkiPathResponse
} from '../types/settings';

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

// Settings-related type guards

export function isSettings(obj: unknown): obj is Settings {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as Settings).anki_db_path === "string" &&
    typeof (obj as Settings).profile === "string" &&
    typeof (obj as Settings).deck_name === "string" &&
    typeof (obj as Settings).api_key_set === "boolean"
  );
}

export function isProfilesResponse(obj: unknown): obj is ProfilesResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    Array.isArray((obj as ProfilesResponse).profiles)
  );
}

export function isDecksResponse(obj: unknown): obj is DecksResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as DecksResponse).decks === "object"
  );
}

export function isAnkiPathResponse(obj: unknown): obj is AnkiPathResponse {
  return (
    typeof obj === "object" &&
    obj !== null &&
    typeof (obj as AnkiPathResponse).anki_db_path === "string" &&
    typeof (obj as AnkiPathResponse).profile === "string" &&
    typeof (obj as AnkiPathResponse).deck_name === "string" &&
    Array.isArray((obj as AnkiPathResponse).profiles) &&
    typeof (obj as AnkiPathResponse).decks === "object"
  );
}
