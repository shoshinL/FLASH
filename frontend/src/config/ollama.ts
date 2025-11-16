/**
 * Ollama Configuration
 *
 * Example models and installation commands for Ollama.
 * These are shown to users when no Ollama models are detected.
 */

export const OLLAMA_EXAMPLES = {
  /** Example LLM models to suggest for installation */
  LLM_MODELS: [
    'llama3.2',
    'deepseek-r1:1.5b',
    'qwen2.5:7b',
  ],

  /** Example embedding models to suggest for installation */
  EMBEDDING_MODELS: [
    'snowflake-arctic-embed2:latest',
    'nomic-embed-text',
    'mxbai-embed-large',
  ],

  /** Command template for installing models */
  INSTALL_COMMAND: 'ollama pull',

  /** Command to start Ollama server */
  START_COMMAND: 'ollama serve',
} as const;
