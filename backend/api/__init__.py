"""
API Module

Provides focused API classes for different application domains:
- AnkiAPI: Anki integration and deck management
- ProviderAPI: LLM provider configuration
- EmbeddingAPI: Embedding provider configuration
- ThinkingAPI: Extended thinking/reasoning configuration
- FlashcardAPI: Flashcard generation and management
"""

from .anki_api import AnkiAPI
from .provider_api import ProviderAPI
from .embedding_api import EmbeddingAPI
from .thinking_api import ThinkingAPI
from .flashcard_api import FlashcardAPI

__all__ = [
    'AnkiAPI',
    'ProviderAPI',
    'EmbeddingAPI',
    'ThinkingAPI',
    'FlashcardAPI'
]
