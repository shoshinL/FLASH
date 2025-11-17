/**
 * Model grouping configuration for organizing models by capability
 */

export const MODEL_GROUPS: Record<string, Record<string, string[]>> = {
  openai: {
    "GPT-4 Models (Latest)": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
    "GPT-4 Models (Legacy)": ["gpt-4", "gpt-4-32k"],
    "GPT-3.5 Models": ["gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
    "Reasoning Models": ["o1", "o1-mini", "o1-preview", "o3-mini"]
  },
  anthropic: {
    "Claude 3.5 Models": ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-20240620", "claude-3-5-haiku-20241022"],
    "Claude 3 Models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
  },
  google: {
    "Gemini 2.0 Models": ["gemini-2.0-flash-exp", "gemini-2.0-flash-thinking-exp"],
    "Gemini 1.5 Models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-flash-8b"],
    "Gemini 1.0 Models": ["gemini-1.0-pro"]
  },
  ollama: {
    "Reasoning Models": ["deepseek-r1", "cogito", "qwq"],
    "Large Models (>7B)": ["llama3.2:70b", "llama3.1:70b", "qwen2.5:14b", "mixtral"],
    "Medium Models (7B)": ["llama3.2:7b", "llama3.1:7b", "mistral", "qwen2.5:7b"],
    "Small Models (<7B)": ["llama3.2:3b", "llama3.2:1b", "deepseek-r1:1.5b", "phi3", "gemma2:2b"]
  }
};

export const EMBEDDING_MODEL_GROUPS: Record<string, Record<string, string[]>> = {
  openai: {
    "OpenAI Embeddings": ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"]
  },
  google: {
    "Gecko Embeddings": ["text-embedding-004", "text-embedding-005"]
  },
  ollama: {
    "Embedding Models": ["snowflake-arctic-embed2", "nomic-embed-text", "mxbai-embed-large", "all-minilm"]
  }
};
