/**
 * Custom hook for fetching available models
 */

import { useState } from 'react';
import { isModelsResponse } from '../utils/typeGuards';

export function useModels() {
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchModels = async (provider: string, isEmbedding: boolean = false) => {
    setLoading(true);
    try {
      const apiMethod = isEmbedding
        ? window.pywebview.api.get_available_embedding_models
        : window.pywebview.api.get_available_models;

      const response: unknown = await apiMethod(provider);

      if (isModelsResponse(response)) {
        if (response.success) {
          setModels(response.models);
          setError(null);
        } else {
          setModels([]);
          if (provider === 'ollama') {
            const modelType = isEmbedding ? 'embedding models' : 'models';
            setError(`⚠️ Ollama is not running or no ${modelType} are installed. Start Ollama with 'ollama serve' and install ${modelType}.`);
          } else {
            setError(response.error || "Failed to fetch models");
          }
        }
      }
    } catch (err) {
      console.error("Error fetching models:", err);
      setModels([]);
      setError("Failed to fetch available models");
    } finally {
      setLoading(false);
    }
  };

  return {
    models,
    loading,
    error,
    setError,
    fetchModels
  };
}
