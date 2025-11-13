/**
 * Unit tests for ProviderSettings component
 *
 * Note: These tests require vitest and @testing-library/react to be installed.
 * Run: npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event
 *
 * To run tests: npm run test
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProviderSettings } from './ProviderSettings';

// Mock pywebview API
const mockApi = {
  get_available_providers: vi.fn(),
  get_provider_config: vi.fn(),
  get_provider_api_keys_status: vi.fn(),
  get_available_models: vi.fn(),
  set_provider_api_key: vi.fn(),
  set_provider_config: vi.fn(),
};

beforeEach(() => {
  // Reset mocks before each test
  vi.clearAllMocks();

  // Mock window.pywebview
  (global as any).window = {
    pywebview: {
      api: mockApi,
    },
  };

  // Setup default mock responses
  mockApi.get_available_providers.mockResolvedValue({
    providers: ['openai', 'anthropic', 'google', 'openrouter', 'ollama'],
  });

  mockApi.get_provider_config.mockResolvedValue({
    provider: 'openai',
    model: 'gpt-4o-mini',
    api_key_set: true,
  });

  mockApi.get_provider_api_keys_status.mockResolvedValue({
    api_keys: { openai: '***xyz' },
    success: true,
  });

  mockApi.get_available_models.mockResolvedValue({
    models: ['gpt-4o', 'gpt-4o-mini', 'o1', 'o3-mini'],
    success: true,
  });
});

describe('ProviderSettings Component', () => {
  describe('Initialization', () => {
    it('should render loading state initially', () => {
      render(<ProviderSettings />);
      expect(screen.getByText(/loading provider settings/i)).toBeInTheDocument();
    });

    it('should fetch provider data on mount', async () => {
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(mockApi.get_available_providers).toHaveBeenCalled();
        expect(mockApi.get_provider_config).toHaveBeenCalled();
        expect(mockApi.get_provider_api_keys_status).toHaveBeenCalled();
      });
    });

    it('should display provider selection dropdown after loading', async () => {
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByText(/Model Provider/i)).toBeInTheDocument();
      });

      const select = screen.getByRole('combobox', { name: /model provider/i });
      expect(select).toBeInTheDocument();
    });
  });

  describe('Provider Selection', () => {
    it('should display all available providers in dropdown', async () => {
      render(<ProviderSettings />);

      await waitFor(() => {
        const select = screen.getByRole('combobox', { name: /model provider/i });
        const options = within(select).getAllByRole('option');

        expect(options).toHaveLength(5);
        expect(options.map(o => o.textContent)).toContain('OpenAI');
        expect(options.map(o => o.textContent)).toContain('Anthropic');
        expect(options.map(o => o.textContent)).toContain('Google (Gemini)');
        expect(options.map(o => o.textContent)).toContain('OpenRouter');
        expect(options.map(o => o.textContent)).toContain('Ollama (Local)');
      });
    });

    it('should change provider when selected', async () => {
      const user = userEvent.setup();
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByRole('combobox', { name: /model provider/i })).toBeInTheDocument();
      });

      const select = screen.getByRole('combobox', { name: /model provider/i });
      await user.selectOptions(select, 'anthropic');

      expect(mockApi.get_available_models).toHaveBeenCalledWith('anthropic');
    });

    it('should hide API key input for Ollama', async () => {
      const user = userEvent.setup();
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByRole('combobox', { name: /model provider/i })).toBeInTheDocument();
      });

      const select = screen.getByRole('combobox', { name: /model provider/i });
      await user.selectOptions(select, 'ollama');

      await waitFor(() => {
        expect(screen.queryByPlaceholderText(/api key/i)).not.toBeInTheDocument();
      });
    });

    it('should show API key input for providers that require it', async () => {
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/openai api key/i)).toBeInTheDocument();
      });
    });
  });

  describe('API Key Management', () => {
    it('should allow setting a new API key', async () => {
      const user = userEvent.setup();
      mockApi.set_provider_api_key.mockResolvedValue({ success: true });

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/openai api key/i)).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/openai api key/i);
      await user.type(input, 'sk-test-key-123');

      const setButton = screen.getByRole('button', { name: /set api key/i });
      await user.click(setButton);

      await waitFor(() => {
        expect(mockApi.set_provider_api_key).toHaveBeenCalledWith('openai', 'sk-test-key-123');
      });
    });

    it('should display success message after setting API key', async () => {
      const user = userEvent.setup();
      mockApi.set_provider_api_key.mockResolvedValue({ success: true });
      mockApi.get_provider_api_keys_status.mockResolvedValueOnce({
        api_keys: { openai: '***123' },
        success: true,
      });

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByPlaceholderText(/openai api key/i)).toBeInTheDocument();
      });

      const input = screen.getByPlaceholderText(/openai api key/i);
      await user.type(input, 'sk-test-key-123');

      const setButton = screen.getByRole('button', { name: /set api key/i });
      await user.click(setButton);

      await waitFor(() => {
        expect(screen.getByText(/api key set successfully/i)).toBeInTheDocument();
      });
    });

    it('should show error when API key is empty', async () => {
      const user = userEvent.setup();
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /set api key/i })).toBeInTheDocument();
      });

      const setButton = screen.getByRole('button', { name: /set api key/i });
      await user.click(setButton);

      await waitFor(() => {
        expect(screen.getByText(/please enter an api key/i)).toBeInTheDocument();
      });
    });
  });

  describe('Model Selection', () => {
    it('should display available models after loading', async () => {
      render(<ProviderSettings />);

      await waitFor(() => {
        const modelSelect = screen.getByRole('combobox', { name: /model/i });
        expect(modelSelect).toBeInTheDocument();

        const options = within(modelSelect).getAllByRole('option');
        expect(options.length).toBeGreaterThan(0);
      });
    });

    it('should update model when selected', async () => {
      const user = userEvent.setup();
      mockApi.set_provider_config.mockResolvedValue({ success: true });

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByRole('combobox', { name: /model/i })).toBeInTheDocument();
      });

      const modelSelect = screen.getByRole('combobox', { name: /model/i });
      await user.selectOptions(modelSelect, 'gpt-4o');

      await waitFor(() => {
        expect(mockApi.set_provider_config).toHaveBeenCalledWith('openai', 'gpt-4o');
      });
    });

    it('should show loading state when fetching models', async () => {
      // Delay the models response
      mockApi.get_available_models.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({
          models: ['gpt-4o'],
          success: true,
        }), 100))
      );

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByText(/loading models/i)).toBeInTheDocument();
      });
    });
  });

  describe('Apply Configuration', () => {
    it('should apply provider configuration when button clicked', async () => {
      const user = userEvent.setup();
      mockApi.set_provider_config.mockResolvedValue({ success: true });

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /apply provider configuration/i })).toBeInTheDocument();
      });

      const applyButton = screen.getByRole('button', { name: /apply provider configuration/i });
      await user.click(applyButton);

      await waitFor(() => {
        expect(mockApi.set_provider_config).toHaveBeenCalled();
      });
    });

    it('should disable apply button when no model is selected', async () => {
      mockApi.get_provider_config.mockResolvedValue({
        provider: 'openai',
        model: null,
        api_key_set: true,
      });

      render(<ProviderSettings />);

      await waitFor(() => {
        const applyButton = screen.getByRole('button', { name: /apply provider configuration/i });
        expect(applyButton).toBeDisabled();
      });
    });
  });

  describe('Error Handling', () => {
    it('should display error message when API call fails', async () => {
      mockApi.get_available_providers.mockRejectedValue(new Error('Network error'));

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByText(/failed to load provider settings/i)).toBeInTheDocument();
      });
    });

    it('should display Ollama-specific error when Ollama is not running', async () => {
      const user = userEvent.setup();
      mockApi.get_available_models.mockResolvedValue({
        models: [],
        success: false,
        error: 'Connection refused',
      });

      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByRole('combobox', { name: /model provider/i })).toBeInTheDocument();
      });

      const select = screen.getByRole('combobox', { name: /model provider/i });
      await user.selectOptions(select, 'ollama');

      await waitFor(() => {
        expect(screen.getByText(/ollama is not running/i)).toBeInTheDocument();
      });
    });
  });

  describe('Provider Information', () => {
    it('should display provider description', async () => {
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByText(/About this provider/i)).toBeInTheDocument();
      });
    });

    it('should update description when provider changes', async () => {
      const user = userEvent.setup();
      render(<ProviderSettings />);

      await waitFor(() => {
        expect(screen.getByText(/OpenAI provides GPT models/i)).toBeInTheDocument();
      });

      const select = screen.getByRole('combobox', { name: /model provider/i });
      await user.selectOptions(select, 'ollama');

      await waitFor(() => {
        expect(screen.getByText(/runs LLM models locally/i)).toBeInTheDocument();
      });
    });
  });
});
