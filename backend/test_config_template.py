"""
Configuration file for backend integration tests.
Copy this file to test_config_local.py and add your real API keys.
test_config_local.py is in .gitignore so your keys won't be committed.
"""

# Provider API Keys - Add your real keys here for testing
API_KEYS = {
    "openai": "",  # Your OpenAI API key (starts with sk-)
    "anthropic": "",  # Your Anthropic API key (starts with sk-ant-)
    "google": "",  # Your Google AI API key
    "openrouter": "",  # Your OpenRouter API key
    "ollama": None,  # No API key needed for Ollama
}

# Models to test for each provider
TEST_MODELS = {
    "openai": "gpt-4.1-2025-04-14",  # Fast and cheap for testing
    "anthropic": "claude-haiku-4-5-20251001",  # Fast and cheap
    "google": "gemini-2.0-flash-lite",  # Fast
    "openrouter": "openai/gpt-4.1",  # Popular model
    "ollama": "cogito:32b",  # Common local model
}

# Thinking models to test (if you have access)
THINKING_MODELS = {
    "openai": "o3-mini-2025-01-31",  # OpenAI reasoning model
    "google": "gemini-2.5-flash-lite",  # Gemini thinking model
    "ollama": "qwen:32b"
}

# Embedding models to test for each provider
# All providers now support embeddings!
TEST_EMBEDDING_MODELS = {
    "openai": "text-embedding-3-small",           # OpenAI embedding
    "anthropic": "voyage-3",                      # Voyage AI (Anthropic partner)
    "google": "models/embedding-001",             # Google embedding
    "openrouter": "qwen/qwen3-embedding-0.6b",    # OpenRouter embedding
    "ollama": "nomic-embed-text",                 # Local Ollama embedding
}

# Test settings
TEST_SETTINGS = {
    "timeout": 30,  # Timeout for API calls in seconds
    "max_retries": 3,  # Max retries for failed tests
    "skip_expensive": True,  # Skip expensive model tests
    "test_thinking_models": False,  # Set to True if you want to test thinking models
}

# Sample test data
TEST_QUESTIONS = [
    "What is the capital of France?",
    "Explain photosynthesis in one sentence.",
    "What is 2 + 2?",
]

TEST_DOCUMENT_CHUNK = """
Machine Learning Basics:
Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.
The three main types are supervised learning, unsupervised learning, and reinforcement learning.
Supervised learning uses labeled data, unsupervised learning finds patterns in unlabeled data, and reinforcement learning learns through trial and error with rewards.
"""
