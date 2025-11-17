"""Ollama (local) provider implementation."""

import logging
import requests
from typing import List, Dict, Optional
from langchain_ollama import ChatOllama, OllamaEmbeddings

from .base import LLMProvider


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
