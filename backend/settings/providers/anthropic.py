"""Anthropic (Claude) provider implementation."""

import logging
from typing import List, Dict, Optional
from langchain_anthropic import ChatAnthropic

from .base import LLMProvider


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
        """
        Thinking controls are always available.
        Best-effort approach: tries to enable reasoning, falls back gracefully.
        """
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

        # Try to enable extended thinking if requested
        if thinking_config and thinking_config.get("enabled"):
            try:
                kwargs["thinking"] = {
                    "type": "enabled",
                    "budget_tokens": thinking_config.get("budget_tokens", 2000)
                }
            except Exception as e:
                logging.debug(f"Extended thinking not supported for {self.model}, continuing without it: {e}")

        return ChatAnthropic(**kwargs)

    def get_available_models(self) -> List[str]:
        """Get available Anthropic models."""
        # If we have an API key, try to fetch models from API
        if self.api_key:
            try:
                from anthropic import Anthropic
                client = Anthropic(api_key=self.api_key)
                models = client.models.list()
                model_ids = [model.id for model in models.data]
                if model_ids:
                    # Sort with popular models first, then alphabetically
                    popular = [m for m in self.POPULAR_MODELS if m in model_ids]
                    other = sorted([m for m in model_ids if m not in self.POPULAR_MODELS])
                    return popular + other
            except Exception as e:
                logging.warning(f"Failed to fetch Anthropic models from API: {e}")

        # Fallback to curated list
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
