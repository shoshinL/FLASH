"""Provider Factory for creating LLM provider instances."""

from typing import List, Optional

from .base import LLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider


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
