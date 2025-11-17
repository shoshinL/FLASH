"""
Base LLM Provider abstract class.
Defines the interface that all provider implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional


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
                    "budget_tokens": int,  # For Claude extended thinking
                    "effort": str,         # For OpenAI reasoning (low/medium/high)
                    "summary": str         # Deprecated (not used - requires org verification)
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
