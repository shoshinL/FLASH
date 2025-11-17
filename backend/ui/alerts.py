"""
UI Alert Functions

Provides custom alert functionality for displaying messages to users
via JavaScript evaluation in the webview.
"""

import json
import webview
from settings.settings_context import SettingsContext


def custom_alert(messages, display_duration=7000) -> str:
    """
    Create JavaScript code to display custom alert messages.

    Args:
        messages: List of message strings to display
        display_duration: How long to show each alert (milliseconds)

    Returns:
        JavaScript code string to evaluate
    """
    # Convert messages list into a JSON string to handle special characters and maintain structure
    messages_json = json.dumps(messages)
    js_code = f"""
    var messages = {messages_json};
    messages.forEach(function(message, index) {{
        var alertDiv = document.createElement('div');
        alertDiv.style.position = 'fixed';
        alertDiv.style.top = (20 + 60 * index) + 'px'; // Offset each alert
        alertDiv.style.left = '50%';
        alertDiv.style.transform = 'translateX(-50%)';
        alertDiv.style.backgroundColor = '#f8d7da';
        alertDiv.style.color = '#721c24';
        alertDiv.style.padding = '10px';
        alertDiv.style.borderRadius = '5px';
        alertDiv.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        alertDiv.style.zIndex = '10000' + index; // Ensure each alert is above the previous
        alertDiv.innerHTML = message;
        document.body.appendChild(alertDiv);
        setTimeout(function() {{ alertDiv.remove(); }}, {display_duration} + 1000 * index); // Staggered removal
    }});
    """
    return js_code


def check_settings(window) -> bool:
    """
    Validate application settings and show alerts for missing configuration.

    Args:
        window: Webview window instance for showing alerts

    Returns:
        True if all settings are valid, False otherwise
    """
    settings_manager = SettingsContext.get_settings_manager()
    settings = settings_manager.get_settings()
    provider_config = settings_manager.get_provider_config()
    embedding_config = settings_manager.get_embedding_config()

    alert_messages = []

    # Check if ANY API key is set or if Ollama is available
    all_api_keys = settings_manager.get_all_provider_api_keys()
    has_any_api_key = len(all_api_keys) > 0

    # Check LLM provider configuration
    provider = provider_config.get('provider', 'openai')
    model = provider_config.get('model')

    # Only check API keys if none are set at all
    if not has_any_api_key and provider != 'ollama':
        alert_messages.append("Please set an API key in the LLM Provider settings to use cloud models, or select Ollama for local models.")
    else:
        # If keys exist, only warn about the SELECTED provider
        if provider != 'ollama':
            api_key = provider_config.get('api_key')
            if not api_key:
                provider_name = provider.capitalize()
                alert_messages.append(f"Please set your {provider_name} API key or switch to a different provider.")

    # Check if LLM model is selected
    if not model:
        alert_messages.append("Please select an LLM model in the Provider settings.")

    # Check embedding provider configuration
    embedding_provider = embedding_config.get('provider')
    embedding_model = embedding_config.get('model')

    # Only warn about embedding provider if it's different from LLM provider and needs a key
    if embedding_provider and embedding_provider != 'ollama' and embedding_provider != provider:
        embedding_api_key = settings_manager.get_provider_api_key(embedding_provider)
        if not embedding_api_key:
            provider_name = embedding_provider.capitalize()
            alert_messages.append(f"Please set your {provider_name} API key for embeddings or use the same provider as your LLM.")

    # Check if embedding model is selected
    if not embedding_model:
        alert_messages.append("Please select an embedding model in the Embedding Provider settings.")

    # Check Anki configuration
    if not settings['anki_data_location_valid']:
        alert_messages.append("Please select a valid Anki database file (prefs21.db) in the Anki Integration settings.")

    if alert_messages:
        window.evaluate_js(custom_alert(alert_messages, 7000))
        return False

    return True


def show_alert_message(message: str, duration: int = 7000):
    """
    Show a single alert message in the webview.

    Args:
        message: Message to display
        duration: How long to show the alert (milliseconds)
    """
    if webview.windows:
        webview.windows[0].evaluate_js(custom_alert([message], duration))
