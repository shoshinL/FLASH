"""
LLM Provider abstraction layer for FLASH.
Supports multiple LLM providers: OpenAI, Anthropic, Google, OpenRouter, and Ollama.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama
import requests


class LLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.temperature = 1e-7  # Default very low temperature for consistency

    @abstractmethod
    def get_llm(self, temperature: Optional[float] = None):
        """Get the LLM instance for this provider."""
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models for this provider."""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key by making a test call."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @property
    @abstractmethod
    def requires_api_key(self) -> bool:
        """Whether this provider requires an API key."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""

    POPULAR_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "o1",
        "o1-mini",
        "o3-mini"
    ]

    @property
    def name(self) -> str:
        return "openai"

    @property
    def requires_api_key(self) -> bool:
        return True

    def get_llm(self, temperature: Optional[float] = None):
        """Get OpenAI LLM instance."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        return ChatOpenAI(
            openai_api_key=self.api_key,
            model=self.model or "gpt-4o-mini",
            temperature=temperature if temperature is not None else self.temperature
        )

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        # For now, return popular models. Could be extended to fetch from API
        return self.POPULAR_MODELS

    def validate_api_key(self) -> bool:
        """Validate OpenAI API key."""
        try:
            llm = self.get_llm()
            llm.invoke("test")
            return True
        except Exception as e:
            logging.error(f"OpenAI API key validation failed: {e}")
            return False


class AnthropicProvider(LLMProvider):
    """Anthropic provider implementation."""

    POPULAR_MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307"
    ]

    @property
    def name(self) -> str:
        return "anthropic"

    @property
    def requires_api_key(self) -> bool:
        return True

    def get_llm(self, temperature: Optional[float] = None):
        """Get Anthropic LLM instance."""
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        return ChatAnthropic(
            anthropic_api_key=self.api_key,
            model=self.model or "claude-3-5-sonnet-20241022",
            temperature=temperature if temperature is not None else self.temperature
        )

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        return self.POPULAR_MODELS

    def validate_api_key(self) -> bool:
        """Validate Anthropic API key."""
        try:
            llm = self.get_llm()
            llm.invoke("test")
            return True
        except Exception as e:
            logging.error(f"Anthropic API key validation failed: {e}")
            return False


class GoogleProvider(LLMProvider):
    """Google (Gemini) provider implementation."""

    POPULAR_MODELS = [
        "gemini-2.0-flash-exp",
        "gemini-2.0-flash-thinking-exp-1219",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b"
    ]

    @property
    def name(self) -> str:
        return "google"

    @property
    def requires_api_key(self) -> bool:
        return True

    def get_llm(self, temperature: Optional[float] = None):
        """Get Google Gemini LLM instance."""
        if not self.api_key:
            raise ValueError("Google API key is required")

        return ChatGoogleGenerativeAI(
            google_api_key=self.api_key,
            model=self.model or "gemini-2.0-flash-exp",
            temperature=temperature if temperature is not None else self.temperature
        )

    def get_available_models(self) -> List[str]:
        """Get available Google models."""
        return self.POPULAR_MODELS

    def validate_api_key(self) -> bool:
        """Validate Google API key."""
        try:
            llm = self.get_llm()
            llm.invoke("test")
            return True
        except Exception as e:
            logging.error(f"Google API key validation failed: {e}")
            return False


class OpenRouterProvider(LLMProvider):
    """OpenRouter provider implementation."""

    POPULAR_MODELS = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "openai/gpt-4o",
        "openai/gpt-4-turbo",
        "google/gemini-2.0-flash-exp",
        "meta-llama/llama-3.1-405b-instruct",
        "deepseek/deepseek-chat",
        "qwen/qwen-2.5-72b-instruct"
    ]

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def requires_api_key(self) -> bool:
        return True

    def get_llm(self, temperature: Optional[float] = None):
        """Get OpenRouter LLM instance."""
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        # OpenRouter uses OpenAI-compatible API
        return ChatOpenAI(
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model=self.model or "anthropic/claude-3.5-sonnet",
            temperature=temperature if temperature is not None else self.temperature
        )

    def get_available_models(self) -> List[str]:
        """Get available OpenRouter models."""
        # Could be extended to fetch from OpenRouter API
        return self.POPULAR_MODELS

    def validate_api_key(self) -> bool:
        """Validate OpenRouter API key."""
        try:
            llm = self.get_llm()
            llm.invoke("test")
            return True
        except Exception as e:
            logging.error(f"OpenRouter API key validation failed: {e}")
            return False


class OllamaProvider(LLMProvider):
    """Ollama (local) provider implementation."""

    DEFAULT_BASE_URL = "http://localhost:11434"

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 base_url: Optional[str] = None):
        super().__init__(api_key, model)
        self.base_url = base_url or self.DEFAULT_BASE_URL

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def requires_api_key(self) -> bool:
        return False

    def get_llm(self, temperature: Optional[float] = None):
        """Get Ollama LLM instance."""
        return ChatOllama(
            model=self.model or "llama3.2",
            temperature=temperature if temperature is not None else self.temperature,
            base_url=self.base_url
        )

    def get_available_models(self) -> List[str]:
        """Get list of locally installed Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models if models else ["llama3.2"]  # Fallback
        except Exception as e:
            logging.error(f"Failed to fetch Ollama models: {e}")
            return ["llama3.2", "mistral", "codellama"]  # Common defaults

    def validate_api_key(self) -> bool:
        """Validate Ollama connection (no API key needed)."""
        try:
            # Just check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Ollama validation failed: {e}")
            return False


class ProviderFactory:
    """Factory class for creating LLM providers."""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "openrouter": OpenRouterProvider,
        "ollama": OllamaProvider
    }

    @staticmethod
    def get_provider(provider_name: str, api_key: Optional[str] = None,
                     model: Optional[str] = None, **kwargs) -> LLMProvider:
        """Create a provider instance by name."""
        provider_class = ProviderFactory.PROVIDERS.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")

        return provider_class(api_key=api_key, model=model, **kwargs)

    @staticmethod
    def get_all_providers() -> List[str]:
        """Get list of all available provider names."""
        return list(ProviderFactory.PROVIDERS.keys())
