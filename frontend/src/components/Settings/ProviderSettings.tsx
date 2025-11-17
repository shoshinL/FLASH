/**
 * Provider Settings Router Component
 *
 * Routes between LLM, Embedding, and API Key settings based on mode.
 */

import { useState, useEffect } from "react";
import "./ProviderSettings.css";

// Custom hooks
import { useProviderConfig, useApiKeys, useModels, useThinkingConfig } from "../../hooks";

// Sub-components
import { LLMSettings } from "./LLMSettings";
import { EmbeddingSettings } from "./EmbeddingSettings";
import { APIKeySettings } from "./APIKeySettings";
import { SettingsLoadingSkeleton } from "../common";

// Utilities
import { isProvidersResponse, isEmbeddingConfig } from "../../utils";

// Constants
import { ERRORS, SUCCESS } from "../../config";

// Types
import type { ProviderMode } from "../../types/provider";

interface ProviderSettingsProps {
  mode: ProviderMode;
}

export function ProviderSettings({ mode }: ProviderSettingsProps) {
  // === Hooks ===
  const llmConfig = useProviderConfig();
  const apiKeysManager = useApiKeys();
  const llmModels = useModels();
  const thinkingConfig = useThinkingConfig();

  // === Local State ===
  const [availableProviders, setAvailableProviders] = useState<string[]>([]);

  // Embedding-specific state
  const [embeddingProviders, setEmbeddingProviders] = useState<string[]>([]);
  const [currentEmbeddingProvider, setCurrentEmbeddingProvider] = useState<string>("openai");
  const [currentEmbeddingModel, setCurrentEmbeddingModel] = useState<string | null>(null);
  const embeddingModels = useModels();
  const [embeddingError, setEmbeddingError] = useState<string | null>(null);
  const [embeddingSuccessMessage, setEmbeddingSuccessMessage] = useState<string | null>(null);

  // === Effects ===
  useEffect(() => {
    fetchProviderData();
  }, []);

  useEffect(() => {
    if (llmConfig.currentProvider) {
      llmModels.fetchModels(llmConfig.currentProvider, false);
    }
  }, [llmConfig.currentProvider]);

  useEffect(() => {
    if (currentEmbeddingProvider) {
      embeddingModels.fetchModels(currentEmbeddingProvider, true);
    }
  }, [currentEmbeddingProvider]);

  useEffect(() => {
    if (llmConfig.currentProvider && llmConfig.currentModel) {
      thinkingConfig.checkThinkingSupport(llmConfig.currentProvider, llmConfig.currentModel);
    }
  }, [llmConfig.currentProvider, llmConfig.currentModel]);

  // === Data Fetching ===
  const fetchProviderData = async () => {
    try {
      const providersResp: unknown = await window.pywebview.api.get_available_providers();
      if (isProvidersResponse(providersResp)) {
        setAvailableProviders(providersResp.providers);
      }

      const embeddingProvidersResp: unknown = await window.pywebview.api.get_embedding_providers();
      if (isProvidersResponse(embeddingProvidersResp)) {
        setEmbeddingProviders(embeddingProvidersResp.providers);
      }

      const embeddingConfigResp: unknown = await window.pywebview.api.get_embedding_config();
      if (isEmbeddingConfig(embeddingConfigResp)) {
        setCurrentEmbeddingProvider(embeddingConfigResp.provider);
        setCurrentEmbeddingModel(embeddingConfigResp.model);
      }

      setEmbeddingError(null);
    } catch (err) {
      console.error("Error fetching provider data:", err);
      llmConfig.setError(ERRORS.PROVIDER_SETTINGS_LOAD);
    }
  };

  // === Event Handlers ===
  const handleProviderChange = async (provider: string) => {
    llmConfig.setCurrentProvider(provider);
    llmConfig.setCurrentModel(null);
    llmConfig.setSuccessMessage(null);
    await llmModels.fetchModels(provider, false);
  };

  const handleModelChange = async (model: string) => {
    await llmConfig.updateProviderConfig(llmConfig.currentProvider, model);
  };

  const handleSetApiKey = async (provider: string, key: string) => {
    const success = await apiKeysManager.setApiKey(provider, key);
    if (success) {
      // Refresh models after setting API key
      if (provider === llmConfig.currentProvider) {
        await llmModels.fetchModels(provider, false);
      }
      if (provider === currentEmbeddingProvider) {
        await embeddingModels.fetchModels(provider, true);
      }
    }
    return success;
  };

  const handleDeleteApiKey = async (provider: string) => {
    const success = await apiKeysManager.deleteApiKey(provider);
    if (success) {
      // Refresh models after deletion
      if (provider === llmConfig.currentProvider) {
        await llmModels.fetchModels(provider, false);
      }
      if (provider === currentEmbeddingProvider) {
        await embeddingModels.fetchModels(provider, true);
      }
    }
    return success;
  };

  const handleEmbeddingProviderChange = async (provider: string) => {
    setCurrentEmbeddingProvider(provider);
    setCurrentEmbeddingModel(null);
    setEmbeddingSuccessMessage(null);
    await embeddingModels.fetchModels(provider, true);
  };

  const handleEmbeddingModelChange = async (model: string) => {
    setCurrentEmbeddingModel(model);
    try {
      const response: unknown = await window.pywebview.api.set_embedding_config(currentEmbeddingProvider, model);
      if (typeof response === "object" && response !== null && "success" in response && response.success) {
        setEmbeddingSuccessMessage(SUCCESS.EMBEDDING_MODEL_UPDATED);
        setTimeout(() => setEmbeddingSuccessMessage(null), 3000);
      } else {
        setEmbeddingError(ERRORS.EMBEDDING_MODEL_SET);
      }
    } catch (err) {
      console.error("Error setting embedding model:", err);
      setEmbeddingError(ERRORS.EMBEDDING_MODEL_SET);
    }
  };

  const handleApplyEmbedding = async () => {
    try {
      const response: unknown = await window.pywebview.api.set_embedding_config(currentEmbeddingProvider, currentEmbeddingModel);
      if (typeof response === "object" && response !== null && "success" in response && response.success) {
        setEmbeddingSuccessMessage(SUCCESS.EMBEDDING_CONFIG_SAVED);
        setTimeout(() => setEmbeddingSuccessMessage(null), 3000);
        setEmbeddingError(null);
      } else {
        const errorMsg = (typeof response === "object" && response !== null && "error" in response)
          ? String(response.error)
          : ERRORS.EMBEDDING_CONFIG_SAVE;
        setEmbeddingError(errorMsg);
      }
    } catch (err) {
      console.error("Error applying embedding config:", err);
      setEmbeddingError(ERRORS.EMBEDDING_CONFIG_SAVE);
    }
  };

  const handleApplyLLM = async () => {
    await llmConfig.updateProviderConfig(llmConfig.currentProvider, llmConfig.currentModel);
  };

  // === Loading State ===
  if (llmConfig.loading || apiKeysManager.loading) {
    return <SettingsLoadingSkeleton />;
  }

  // === Route to Appropriate Component ===
  if (mode === "llm") {
    return (
      <LLMSettings
        currentProvider={llmConfig.currentProvider}
        currentModel={llmConfig.currentModel}
        availableProviders={availableProviders}
        models={llmModels.models}
        modelsLoading={llmModels.loading}
        supportsThinking={thinkingConfig.supportsThinking}
        thinkingEnabled={thinkingConfig.enabled}
        thinkingBudgetTokens={thinkingConfig.budgetTokens}
        thinkingEffort={thinkingConfig.effort}
        apiKeys={apiKeysManager.apiKeys}
        error={llmConfig.error}
        successMessage={llmConfig.successMessage}
        onProviderChange={handleProviderChange}
        onModelChange={handleModelChange}
        onUpdateThinkingConfig={thinkingConfig.updateThinkingConfig}
        onApply={handleApplyLLM}
      />
    );
  }

  if (mode === "api_keys") {
    return (
      <APIKeySettings
        availableProviders={availableProviders}
        apiKeys={apiKeysManager.apiKeys}
        error={apiKeysManager.error}
        successMessage={apiKeysManager.successMessage}
        onSetApiKey={handleSetApiKey}
        onDeleteApiKey={handleDeleteApiKey}
      />
    );
  }

  // Default: Embedding settings
  return (
    <EmbeddingSettings
      currentProvider={currentEmbeddingProvider}
      currentModel={currentEmbeddingModel}
      embeddingProviders={embeddingProviders}
      models={embeddingModels.models}
      modelsLoading={embeddingModels.loading}
      apiKeys={apiKeysManager.apiKeys}
      error={embeddingError}
      successMessage={embeddingSuccessMessage}
      onProviderChange={handleEmbeddingProviderChange}
      onModelChange={handleEmbeddingModelChange}
      onApply={handleApplyEmbedding}
    />
  );
}
