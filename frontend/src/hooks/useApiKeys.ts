/**
 * Custom hook for managing API keys
 */

import { useState, useEffect } from 'react';
import { isApiKeysStatusResponse } from '../utils/typeGuards';
import { PROVIDER_DISPLAY_NAMES } from '../config/providers';
import { TIMEOUTS, ERRORS, SUCCESS } from '../config';

export function useApiKeys() {
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  useEffect(() => {
    fetchApiKeys();
  }, []);

  const fetchApiKeys = async () => {
    setLoading(true);
    try {
      const keysResp: unknown = await window.pywebview.api.get_provider_api_keys_status();
      if (isApiKeysStatusResponse(keysResp)) {
        setApiKeys(keysResp.api_keys);
      }
      setError(null);
    } catch (err) {
      console.error("Error fetching API keys:", err);
      setError(ERRORS.API_KEY_LOAD);
    } finally {
      setLoading(false);
    }
  };

  const setApiKey = async (provider: string, apiKey: string) => {
    try {
      const response: unknown = await window.pywebview.api.set_provider_api_key(provider, apiKey);

      if (
        typeof response === "object" &&
        response !== null &&
        "success" in response &&
        response.success
      ) {
        await fetchApiKeys();
        setSuccessMessage(SUCCESS.API_KEY_SET(PROVIDER_DISPLAY_NAMES[provider]));
        setTimeout(() => setSuccessMessage(null), TIMEOUTS.SUCCESS_MESSAGE);
        setError(null);
        return true;
      } else {
        setError(ERRORS.API_KEY_SET);
        return false;
      }
    } catch (err) {
      console.error("Error setting API key:", err);
      setError(ERRORS.API_KEY_SET);
      return false;
    }
  };

  const deleteApiKey = async (provider: string) => {
    try {
      const response: unknown = await window.pywebview.api.delete_provider_api_key(provider);

      if (
        typeof response === "object" &&
        response !== null &&
        "success" in response &&
        response.success
      ) {
        await fetchApiKeys();
        setSuccessMessage(SUCCESS.API_KEY_DELETED(PROVIDER_DISPLAY_NAMES[provider]));
        setTimeout(() => setSuccessMessage(null), TIMEOUTS.SUCCESS_MESSAGE);
        setError(null);
        return true;
      } else {
        setError(ERRORS.API_KEY_DELETE);
        return false;
      }
    } catch (err) {
      console.error("Error deleting API key:", err);
      setError(ERRORS.API_KEY_DELETE);
      return false;
    }
  };

  return {
    apiKeys,
    loading,
    error,
    successMessage,
    setError,
    setSuccessMessage,
    setApiKey,
    deleteApiKey,
    fetchApiKeys
  };
}
