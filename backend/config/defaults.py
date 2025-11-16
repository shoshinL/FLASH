"""
Backend Configuration - Default Values

Centralized configuration for default models, thinking settings,
and other backend constants.
"""

from typing import Dict, Any

# ============ Default Models by Provider ============

DEFAULT_MODELS: Dict[str, Dict[str, str]] = {
    'openai': {
        'llm': 'gpt-4o-mini',
        'embedding': 'text-embedding-3-small'
    },
    'anthropic': {
        'llm': 'claude-3-5-sonnet-20241022',
        'embedding': None  # Anthropic doesn't provide embeddings
    },
    'google': {
        'llm': 'gemini-2.0-flash-exp',
        'embedding': 'models/embedding-001'
    },
    'ollama': {
        'llm': 'llama3.2',
        'embedding': 'nomic-embed-text'
    },
    'openrouter': {
        'llm': None,  # User must select
        'embedding': None
    }
}

# ============ Thinking Configuration ============

THINKING_CONFIG: Dict[str, Any] = {
    # Default thinking budget in tokens (for providers like Claude)
    'default_budget_tokens': 2000,

    # Minimum allowed thinking budget
    'min_budget_tokens': 500,

    # Maximum allowed thinking budget
    'max_budget_tokens': 10000,

    # Default reasoning effort (for providers like OpenAI: low, medium, high)
    'default_effort': 'medium',

    # Default summary setting
    'default_summary': 'auto',
}

# ============ Ollama Configuration ============

OLLAMA_CONFIG: Dict[str, Any] = {
    # Default base URL for local Ollama instance
    'default_base_url': 'http://localhost:11434',

    # Health check endpoint
    'health_check_endpoint': '/api/tags',

    # Expected HTTP status code for successful health check
    'success_status_code': 200,

    # Request timeout in seconds
    'timeout': 5,
}

# ============ Alert/Notification Configuration ============

ALERT_CONFIG: Dict[str, Any] = {
    # Default alert display duration in milliseconds
    'default_duration': 7000,

    # Vertical offset from top of screen (pixels)
    'vertical_offset': 20,

    # Spacing between multiple alerts (pixels)
    'spacing': 60,

    # Base z-index for alerts
    'z_index_base': 10000,

    # Delay between showing multiple alerts (milliseconds)
    'stagger_delay': 1000,
}

# ============ Progress Bar Configuration ============

PROGRESS_CONFIG: Dict[str, Any] = {
    # Total steps in flashcard generation process
    'total_steps': 5,

    # Progress increment per step (percentage)
    'step_increment': 20,

    # Final progress value (percentage)
    'final_progress': 100,
}

# ============ Cost Estimation ============

COST_CONFIG: Dict[str, float] = {
    # Approximate cost per million tokens for thinking (USD)
    # This is a rough estimate and may vary by provider
    'per_million_tokens': 4.0,
}
