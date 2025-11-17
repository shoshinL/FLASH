"""
LLM and Embedding Provider abstraction layer for FLASH.

This module provides backward compatibility by re-exporting from the providers package.
All provider implementations have been moved to settings/providers/ for better organization.

New code should import directly from settings.providers:
    from settings.providers import ProviderFactory, OpenAIProvider, etc.

This file maintains backward compatibility with existing imports:
    from settings.llm_provider import ProviderFactory  # Still works
"""

# Re-export everything from providers package for backward compatibility
from .providers import (
    LLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    OpenRouterProvider,
    OllamaProvider,
    ProviderFactory
)

__all__ = [
    'LLMProvider',
    'OpenAIProvider',
    'AnthropicProvider',
    'GoogleProvider',
    'OpenRouterProvider',
    'OllamaProvider',
    'ProviderFactory'
]
