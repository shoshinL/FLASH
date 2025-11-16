"""
LLM and Embedding Provider abstraction layer for FLASH.
Supports multiple providers: OpenAI, Anthropic, Google, OpenRouter, and Ollama.
Includes both LLM and embedding model support.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_voyageai import VoyageAIEmbeddings
import requests


class LLMProvider(ABC):
    """Base class for LLM and embedding providers."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 embedding_model: Optional[str] = None):
        self.api_key = api_key
        self.model = model
        self.embedding_model = embedding_model
        self.temperature = 1e-7  # Default very low temperature for consistency

    @abstractmethod
    def get_llm(self, temperature: Optional[float] = None, thinking_config: Optional[Dict] = None):
        """
        Get the LLM instance for this provider.

        Args:
            temperature: Optional temperature override
            thinking_config: Optional thinking/reasoning configuration
                {
                    "enabled": bool,
                    "budget_tokens": int,  # For Claude
                    "effort": str,         # For OpenAI (low/medium/high)
                    "summary": str         # For OpenAI (auto/concise/detailed)
                }
        """
        pass

    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available LLM models for this provider."""
        pass

    @abstractmethod
    def get_available_embedding_models(self) -> List[str]:
        """Get list of available embedding models for this provider."""
        pass

    @abstractmethod
    def get_embeddings(self, model: Optional[str] = None):
        """Get embeddings instance for this provider."""
        pass

    @abstractmethod
    def supports_embeddings(self) -> bool:
        """Whether this provider supports embeddings."""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate the API key by making a test call."""
        pass

    @abstractmethod
    def supports_thinking(self) -> bool:
        """Whether this provider/model supports thinking/reasoning controls."""
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

    EMBEDDING_MODELS = [
        "text-embedding-3-large",
        "text-embedding-3-small",
        "text-embedding-ada-002"
    ]

    @property
    def name(self) -> str:
        return "openai"

    @property
    def requires_api_key(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return True

    def supports_thinking(self) -> bool:
        """OpenAI o-series models support reasoning controls."""
        model = self.model or "gpt-4o-mini"
        reasoning_models = ["o1", "o1-mini", "o1-preview", "o3-mini"]
        return any(model.startswith(rm) for rm in reasoning_models)

    def get_llm(self, temperature: Optional[float] = None, thinking_config: Optional[Dict] = None):
        """Get OpenAI LLM instance."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        model = self.model or "gpt-4o-mini"

        # Reasoning models (o1, o3-mini, etc.) don't support temperature parameter
        reasoning_models = ["o1", "o1-mini", "o1-preview", "o3-mini"]
        is_reasoning_model = any(model.startswith(rm) for rm in reasoning_models)

        kwargs = {
            "openai_api_key": self.api_key,
            "model": model,
        }

        # Reasoning models get reasoning config if enabled
        if is_reasoning_model and thinking_config and thinking_config.get("enabled"):
            # OpenAI reasoning models support 'reasoning' parameter
            kwargs["reasoning"] = {
                "effort": thinking_config.get("effort", "medium"),
                "summary": thinking_config.get("summary", "auto")
            }
        # Standard models get temperature
        elif not is_reasoning_model:
            kwargs["temperature"] = temperature if temperature is not None else self.temperature

        return ChatOpenAI(**kwargs)

    def get_available_models(self) -> List[str]:
        """Get available OpenAI models."""
        return self.POPULAR_MODELS

    def get_available_embedding_models(self) -> List[str]:
        """Get available OpenAI embedding models."""
        return self.EMBEDDING_MODELS

    def get_embeddings(self, model: Optional[str] = None):
        """Get OpenAI embeddings instance."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        return OpenAIEmbeddings(
            openai_api_key=self.api_key,
            model=model or self.embedding_model or "text-embedding-3-small"
        )

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

    def supports_embeddings(self) -> bool:
        return False  # Anthropic doesn't provide embeddings

    def supports_thinking(self) -> bool:
        """All Claude models support extended thinking."""
        return True

    def get_llm(self, temperature: Optional[float] = None, thinking_config: Optional[Dict] = None):
        """Get Anthropic LLM instance."""
        if not self.api_key:
            raise ValueError("Anthropic API key is required")

        kwargs = {
            "anthropic_api_key": self.api_key,
            "model": self.model or "claude-3-5-sonnet-20241022",
            "temperature": temperature if temperature is not None else self.temperature
        }

        # Add extended thinking if enabled
        if thinking_config and thinking_config.get("enabled"):
            kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_config.get("budget_tokens", 2000)
            }

        return ChatAnthropic(**kwargs)

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        return self.POPULAR_MODELS

    def get_available_embedding_models(self) -> List[str]:
        """Anthropic doesn't provide embedding models."""
        return []

    def get_embeddings(self, model: Optional[str] = None):
        """Anthropic doesn't provide embeddings."""
        raise NotImplementedError("Anthropic does not provide embedding models")

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

    EMBEDDING_MODELS = [
        "models/embedding-001",
        "models/text-embedding-004"
    ]

    THINKING_MODELS = [
        "gemini-2.0-flash-thinking-exp-1219",
        "gemini-2.0-flash-thinking-exp",
        "gemini-2.5-flash-lite"
    ]

    @property
    def name(self) -> str:
        return "google"

    @property
    def requires_api_key(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return True

    def supports_thinking(self) -> bool:
        """Specific Gemini models support thinking mode."""
        model = self.model or "gemini-2.0-flash-exp"
        return model in self.THINKING_MODELS or "thinking" in model.lower()

    def get_llm(self, temperature: Optional[float] = None, thinking_config: Optional[Dict] = None):
        """Get Google Gemini LLM instance."""
        if not self.api_key:
            raise ValueError("Google API key is required")

        kwargs = {
            "google_api_key": self.api_key,
            "model": self.model or "gemini-2.0-flash-exp",
            "temperature": temperature if temperature is not None else self.temperature
        }

        # Note: Google's thinking mode is model-specific, enabled by using thinking models
        # No additional configuration parameters needed beyond model selection

        return ChatGoogleGenerativeAI(**kwargs)

    def get_available_models(self) -> List[str]:
        """Get available Google models."""
        return self.POPULAR_MODELS

    def get_available_embedding_models(self) -> List[str]:
        """Get available Google embedding models."""
        return self.EMBEDDING_MODELS

    def get_embeddings(self, model: Optional[str] = None):
        """Get Google embeddings instance."""
        if not self.api_key:
            raise ValueError("Google API key is required")

        return GoogleGenerativeAIEmbeddings(
            google_api_key=self.api_key,
            model=model or self.embedding_model or "models/embedding-001"
        )

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

    EMBEDDING_MODELS = [
        "qwen/qwen3-embedding-0.6b",
        "snowflake/snowflake-arctic-embed-l-v2.0",
        "BAAI/bge-m3",
        "nvidia/nv-embedqa-e5-v5"
    ]

    @property
    def name(self) -> str:
        return "openrouter"

    @property
    def requires_api_key(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return True  # OpenRouter now provides embeddings

    def supports_thinking(self) -> bool:
        """OpenRouter thinking support depends on underlying model (complex to determine)."""
        # For simplicity, return False for now
        # Users can select thinking-capable models through the provider
        return False

    def get_llm(self, temperature: Optional[float] = None, thinking_config: Optional[Dict] = None):
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
        return self.POPULAR_MODELS

    def get_available_embedding_models(self) -> List[str]:
        """Get available OpenRouter embedding models."""
        return self.EMBEDDING_MODELS

    def get_embeddings(self, model: Optional[str] = None):
        """Get OpenRouter embeddings instance (OpenAI-compatible API)."""
        if not self.api_key:
            raise ValueError("OpenRouter API key is required")

        # OpenRouter uses OpenAI-compatible API for embeddings
        return OpenAIEmbeddings(
            openai_api_key=self.api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model=model or self.embedding_model or "qwen/qwen3-embedding-0.6b"
        )

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
                 embedding_model: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, model, embedding_model)
        self.base_url = base_url or self.DEFAULT_BASE_URL

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def requires_api_key(self) -> bool:
        return False

    def supports_embeddings(self) -> bool:
        return True

    def supports_thinking(self) -> bool:
        """Ollama supports thinking for qwen models and models with 'think' in name."""
        model = self.model or "llama3.2"
        return "qwen" in model.lower() or "think" in model.lower()

    def get_llm(self, temperature: Optional[float] = None, thinking_config: Optional[Dict] = None):
        """Get Ollama LLM instance."""
        kwargs = {
            "model": self.model or "llama3.2",
            "temperature": temperature if temperature is not None else self.temperature,
            "base_url": self.base_url
        }

        # Note: Ollama thinking support is model-specific
        # Some models like qwen support thinking mode natively
        # The --think flag is a CLI parameter, not API parameter
        # Thinking behavior is controlled by the model itself

        return ChatOllama(**kwargs)

    def get_available_models(self) -> List[str]:
        """Get list of locally installed Ollama models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            models = [model['name'] for model in data.get('models', [])]
            return models if models else ["llama3.2"]
        except Exception as e:
            logging.error(f"Failed to fetch Ollama models: {e}")
            return ["llama3.2", "mistral", "codellama"]

    def get_available_embedding_models(self) -> List[str]:
        """Get list of locally installed Ollama embedding models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            data = response.json()
            # Filter for common embedding models
            all_models = [model['name'] for model in data.get('models', [])]
            # Common embedding model names
            embedding_keywords = ['embed', 'embedding', 'nomic', 'snowflake', 'mxbai']
            embedding_models = [m for m in all_models if any(k in m.lower() for k in embedding_keywords)]

            # If no embedding models found, return common defaults
            if not embedding_models:
                return ["nomic-embed-text", "snowflake-arctic-embed2", "mxbai-embed-large"]

            return embedding_models
        except Exception as e:
            logging.error(f"Failed to fetch Ollama embedding models: {e}")
            return ["nomic-embed-text", "snowflake-arctic-embed2", "mxbai-embed-large"]

    def get_embeddings(self, model: Optional[str] = None):
        """Get Ollama embeddings instance."""
        return OllamaEmbeddings(
            model=model or self.embedding_model or "nomic-embed-text",
            base_url=self.base_url
        )

    def validate_api_key(self) -> bool:
        """Validate Ollama connection (no API key needed)."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Ollama validation failed: {e}")
            return False


class ProviderFactory:
    """Factory class for creating LLM and embedding providers."""

    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "google": GoogleProvider,
        "openrouter": OpenRouterProvider,
        "ollama": OllamaProvider
    }

    @staticmethod
    def get_provider(provider_name: str, api_key: Optional[str] = None,
                     model: Optional[str] = None, embedding_model: Optional[str] = None,
                     **kwargs) -> LLMProvider:
        """Create a provider instance by name."""
        provider_class = ProviderFactory.PROVIDERS.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}")

        return provider_class(api_key=api_key, model=model,
                            embedding_model=embedding_model, **kwargs)

    @staticmethod
    def get_all_providers() -> List[str]:
        """Get list of all available provider names."""
        return list(ProviderFactory.PROVIDERS.keys())

    @staticmethod
    def get_embedding_providers() -> List[str]:
        """Get list of providers that support embeddings."""
        return ["openai", "google", "openrouter", "ollama"]
