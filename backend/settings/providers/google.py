"""Google (Gemini) provider implementation."""

import logging
from typing import List, Dict, Optional
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from .base import LLMProvider


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

    @property
    def name(self) -> str:
        return "google"

    @property
    def requires_api_key(self) -> bool:
        return True

    def supports_embeddings(self) -> bool:
        return True

    def supports_thinking(self) -> bool:
        """
        Thinking controls are always available.
        Models with 'thinking' in name use it automatically (model-intrinsic).
        """
        return True  # Always show UI controls

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
        # If we have an API key, try to fetch models from API
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                models = genai.list_models()

                # Exclude these types from chat models
                excluded_keywords = ['computer-use', 'robotics', 'image', 'tts', 'embedding']

                # Filter for chat/generation models (generateContent capability)
                model_ids = []
                for model in models:
                    # Must have generateContent capability
                    if 'generateContent' not in model.supported_generation_methods:
                        continue
                    # Must start with gemini-
                    model_id = model.name.replace('models/', '')
                    if not model_id.startswith('gemini-'):
                        continue
                    # Exclude models with excluded keywords
                    if any(keyword in model_id.lower() for keyword in excluded_keywords):
                        continue
                    model_ids.append(model_id)

                if model_ids:
                    # Sort with popular models first, then alphabetically
                    popular = [m for m in self.POPULAR_MODELS if m in model_ids]
                    other = sorted([m for m in model_ids if m not in self.POPULAR_MODELS])
                    return popular + other
            except Exception as e:
                logging.warning(f"Failed to fetch Google models from API: {e}")

        # Fallback to curated list
        return self.POPULAR_MODELS

    def get_available_embedding_models(self) -> List[str]:
        """Get available Google embedding models."""
        # If we have an API key, try to fetch embedding models from API
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                models = genai.list_models()

                # Filter for embedding models (embedContent capability)
                model_ids = [
                    model.name  # Keep the 'models/' prefix for embeddings
                    for model in models
                    if 'embedContent' in model.supported_generation_methods
                ]

                if model_ids:
                    # Sort with popular models first, then alphabetically
                    popular = [m for m in self.EMBEDDING_MODELS if m in model_ids]
                    other = sorted([m for m in model_ids if m not in self.EMBEDDING_MODELS])
                    return popular + other
            except Exception as e:
                logging.warning(f"Failed to fetch Google embedding models from API: {e}")

        # Fallback to curated list
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
