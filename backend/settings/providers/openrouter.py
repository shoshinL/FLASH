"""OpenRouter provider implementation."""

import logging
import requests
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .base import LLMProvider


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
        # If we have an API key, try to fetch models from API
        if self.api_key:
            try:
                response = requests.get(
                    "https://openrouter.ai/api/v1/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=5
                )
                response.raise_for_status()
                data = response.json()
                model_ids = [model['id'] for model in data.get('data', [])]
                if model_ids:
                    # Sort with popular models first, then alphabetically
                    popular = [m for m in self.POPULAR_MODELS if m in model_ids]
                    other = sorted([m for m in model_ids if m not in self.POPULAR_MODELS])
                    return popular + other
            except Exception as e:
                logging.warning(f"Failed to fetch OpenRouter models from API: {e}")

        # Fallback to curated list
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
