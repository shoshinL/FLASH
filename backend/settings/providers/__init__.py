"""
LLM and Embedding Provider abstraction layer for FLASH.
Supports multiple providers: OpenAI, Anthropic, Google, OpenRouter, and Ollama.
"""

from .base import LLMProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider
from .openrouter import OpenRouterProvider
from .ollama import OllamaProvider
from .factory import ProviderFactory

__all__ = [
    'LLMProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'OpenRouterProvider',
    'OllamaProvider',
    'ProviderFactory'
]
