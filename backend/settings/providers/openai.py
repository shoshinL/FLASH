"""OpenAI provider implementation."""

import logging
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .base import LLMProvider


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
            # Note: 'summary' requires organization verification, so we skip it
            kwargs["reasoning"] = {
                "effort": thinking_config.get("effort", "medium")
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
