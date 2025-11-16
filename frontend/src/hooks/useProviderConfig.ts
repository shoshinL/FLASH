/**
 * Custom hook for managing provider configuration
 */

import { useState, useEffect } from 'react';
import { isProviderConfig } from '../utils/typeGuards';
import { TIMEOUTS, ERRORS, SUCCESS } from '../config';

export function useProviderConfig() {
  const [currentProvider, setCurrentProvider] = useState<string>("openai");
  const [currentModel, setCurrentModel] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchProviderConfig();
  }, []);

  const fetchProviderConfig = async () => {
    setLoading(true);
    try {
      const configResp: unknown = await window.pywebview.api.get_provider_config();
      if (isProviderConfig(configResp)) {
        setCurrentProvider(configResp.provider);
        setCurrentModel(configResp.model);
      }
      setError(null);
    } catch (err) {
      console.error("Error fetching provider config:", err);
      setError(ERRORS.PROVIDER_CONFIG_LOAD);
    } finally {
      setLoading(false);
    }
  };

  const updateProviderConfig = async (provider: string, model: string | null) => {
    try {
      await window.pywebview.api.set_provider_config(provider, model);
      setCurrentProvider(provider);
      setCurrentModel(model);
      setSuccessMessage(SUCCESS.PROVIDER_CONFIG_SAVED);
      setTimeout(() => setSuccessMessage(null), TIMEOUTS.SUCCESS_MESSAGE);
      setError(null);
    } catch (err) {
      console.error("Error saving provider config:", err);
      setError(ERRORS.PROVIDER_CONFIG_SAVE);
    }
  };

  return {
    currentProvider,
    currentModel,
    loading,
    error,
    successMessage,
    setCurrentProvider,
    setCurrentModel,
    setError,
    setSuccessMessage,
    updateProviderConfig,
    fetchProviderConfig
  };
}
