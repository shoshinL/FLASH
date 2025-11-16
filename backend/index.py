import json
import os
import random
import time
import webview
import logging
import sys
from anki.errors import DBError

from settings.settings_manager import SettingsManager
from settings.settings_context import SettingsContext
from agents.note_graph import graph

# Configure logging to show only our app's debug messages, not external libraries
logging.basicConfig(level=logging.INFO,  # Set root logger to INFO
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

# Set our application modules to DEBUG level
logging.getLogger('settings').setLevel(logging.DEBUG)
logging.getLogger('agents').setLevel(logging.DEBUG)
logging.getLogger('anki').setLevel(logging.DEBUG)
logging.getLogger(__name__).setLevel(logging.DEBUG)

# Silence noisy external libraries
logging.getLogger('httpcore').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('ollama').setLevel(logging.WARNING)
logging.getLogger('langchain').setLevel(logging.WARNING)
logging.getLogger('chromadb').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def custom_alert(messages, display_duration=7000) -> str:
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

def check_settings(window):
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


class Api:
    def show_alert(self, message):
        webview.windows[0].evaluate_js(custom_alert([message], 7000))

    def valid_settings(self):
        return check_settings(webview.windows[0])

    def select_file(self):
        file_types = ('PDF Files (*.pdf)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, file_types=file_types, allow_multiple=False)
        if result:
            return result[0]
        return None
        
    def generate_flashcards_test(self, content, file_path, card_amount):
            def generate_updates():
                total_steps = 5
                flashcard_types = ['Basic', 'Basic (and reversed card)', 'Basic (type in the answer)', 'Cloze']
                
                for step in range(1, total_steps + 1):
                    progress = (step / total_steps) * 100
                    if step == 1:
                        yield {"progress": progress, "message": "Processing document..."}
                    elif step == 2:
                        yield {"progress": progress, "message": "Analyzing content..."}
                    elif step == 3:
                        yield {"progress": progress, "message": "Generating flashcards..."}
                    elif step == 4:
                        yield {"progress": progress, "message": "Finalizing results..."}
                    else:
                        flashcards = []
                        for i in range(1, int(card_amount) + 1):
                            card_type = random.choice(flashcard_types)
                            if card_type == 'Basic':
                                flashcards.append({
                                    "Type": "Basic",
                                    "Front": f"Question {i} from {content}",
                                    "Back": f"Answer {i} for {file_path}"
                                })
                            elif card_type == 'Basic (and reversed card)':
                                flashcards.append({
                                    "Type": "Basic (and reversed card)",
                                    "Front": f"Term {i} from {content}",
                                    "Back": f"Definition {i} for {file_path}"
                                })
                            elif card_type == 'Basic (type in the answer)':
                                flashcards.append({
                                    "Type": "Basic (type in the answer)",
                                    "Front": f"Type the answer for Question {i} from {content}",
                                    "Back": f"Answer{i}"
                                })
                            elif card_type == 'Cloze':
                                flashcards.append({
                                    "Type": "Cloze",
                                    "Text": f"{{{{c1::{content}}}}} is related to {{{{c2::{file_path}}}}} in concept {i}",
                                    "BackExtra": f"Additional info for concept {i}"
                                })
                        
                        results = {"flashcards": flashcards, "filename": os.path.basename(file_path)}
                        yield {"progress": progress, "message": "Complete!", "result": results}
                    
                    time.sleep(1)  # Simulate processing time

            for update in generate_updates():
                webview.windows[0].evaluate_js(f"window.dispatchEvent(new CustomEvent('backendUpdate', {{detail: {json.dumps(update)}}}));")
            
            return "Flashcard generation test completed"

    def generate_flashcards(self, content, file_path, card_amount):
        last_step = ""
        progress = 0

        for state in graph.stream({"questioning_context": content, "documentpath": file_path, "n_questions": card_amount}):
            key = next(iter(state))
            try:
                current_step = state[key]["current_step"]
            except:
                continue

            if current_step != last_step:
                logger.debug(f"Current step in graph: {current_step}")
                last_step = current_step
                progress += 20
                update = {"progress": progress, "message": current_step}
                if current_step == "Finished!":
                    flashcards = state[key]["notes"]
                    filename = os.path.basename(state[key]["documentpath"])
                    update = {
                        "progress": 100,
                        "message": "Complete!",
                        "result": {"flashcards":flashcards, "filename":filename}
                    }
                webview.windows[0].evaluate_js(f"window.dispatchEvent(new CustomEvent('backendUpdate', {{detail: {json.dumps(update)}}}));")

        return "Flashcard generation completed"

    def save_accepted_flashcards(self, flashcards, filename):
        if not flashcards:
            return "ERROR"
        try:
            settings_manager.add_generated_cards_to_deck(filename, flashcards)
            return "Success!!"
        except Exception as e:
            print(f"Error saving flashcards: {e}")
            return "ERROR"

    def get_settings(self):
        return SettingsContext.get_settings_manager().get_settings()

    def get_profiles(self, anki_db_path):
        profiles = SettingsContext.get_settings_manager().get_profiles(anki_db_path)
        return {"profiles": profiles}

    def get_decks(self, profile):
        decks = SettingsContext.get_settings_manager().get_decks(profile)
        return {"decks": decks}
    
    def get_selected_deck(self):
        return SettingsContext.get_settings_manager().deck_name
    
    def get_selected_profile(self):
        return SettingsContext.get_settings_manager().profile

    def select_file_path(self):
        file_types = ('Database Files (*.db)',)
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        if result and result[0]:
            return SettingsContext.get_settings_manager().upsert_anki_db_path(result[0])
        return {"error": "No file selected"}

    def set_profile(self, profile):
        return SettingsContext.get_settings_manager().upsert_profile(profile)

    def set_deck(self, deck_name):
        SettingsContext.get_settings_manager().upsert_deck_name(deck_name)
        return {"success": True, "deck_name": deck_name}

    def set_api_key(self, api_key):
        success = SettingsContext.get_settings_manager().set_api_key(api_key)
        return {"success": success, "api_key_set": SettingsContext.get_settings_manager().api_key_exists()}

    # ========== Provider Management API Endpoints ==========

    def get_available_providers(self):
        """Get list of all available LLM providers."""
        from settings.llm_provider import ProviderFactory
        providers = ProviderFactory.get_all_providers()
        return {"providers": providers}

    def get_provider_config(self):
        """Get current provider configuration."""
        config = SettingsContext.get_settings_manager().get_provider_config()
        # Don't send the actual API key, just whether it's set
        return {
            "provider": config.get("provider", "openai"),
            "model": config.get("model"),
            "api_key_set": config.get("api_key") is not None
        }

    def get_available_models(self, provider):
        """Get available models for a specific provider."""
        from settings.llm_provider import ProviderFactory
        try:
            settings_manager = SettingsContext.get_settings_manager()
            api_key = settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider)
            else:
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key)

            models = provider_instance.get_available_models()
            return {"models": models, "success": True}
        except Exception as e:
            logger.error(f"Error fetching models for {provider}: {e}")
            return {"models": [], "success": False, "error": str(e)}

    def set_provider_api_key(self, provider, api_key):
        """Set API key for a specific provider."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_provider_api_key(provider, api_key)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting API key for {provider}: {e}")
            return {"success": False, "error": str(e)}

    def delete_provider_api_key(self, provider):
        """Delete API key for a specific provider."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.delete_provider_api_key(provider)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error deleting API key for {provider}: {e}")
            return {"success": False, "error": str(e)}

    def get_provider_api_keys_status(self):
        """Get status of which providers have API keys set."""
        settings_manager = SettingsContext.get_settings_manager()
        masked_keys = settings_manager.get_all_provider_api_keys()
        return {
            "api_keys": masked_keys,
            "success": True
        }

    def set_provider_config(self, provider, model=None):
        """Set the current provider and model."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_provider_config(provider, model)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting provider config: {e}")
            return {"success": False, "error": str(e)}

    def validate_provider(self, provider, api_key=None, model=None):
        """Validate a provider configuration."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            is_valid = settings_manager.validate_provider(provider, api_key, model)
            return {"valid": is_valid, "success": True}
        except Exception as e:
            logger.error(f"Error validating provider {provider}: {e}")
            return {"valid": False, "success": False, "error": str(e)}

    # ========== Embedding Configuration API Endpoints ==========

    def get_embedding_providers(self):
        """Get list of providers that support embeddings."""
        from settings.llm_provider import ProviderFactory
        try:
            providers = ProviderFactory.get_embedding_providers()
            return {"providers": providers, "success": True}
        except Exception as e:
            logger.error(f"Error getting embedding providers: {e}")
            return {"providers": [], "success": False, "error": str(e)}

    def get_embedding_config(self):
        """Get current embedding configuration."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            config = settings_manager.get_embedding_config()
            # Don't send the actual API key, just whether it's set
            return {
                "provider": config.get("provider", "openai"),
                "model": config.get("model"),
                "api_key_set": config.get("api_key") is not None,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error getting embedding config: {e}")
            return {"success": False, "error": str(e)}

    def get_available_embedding_models(self, provider):
        """Get available embedding models for a specific provider."""
        from settings.llm_provider import ProviderFactory
        try:
            settings_manager = SettingsContext.get_settings_manager()
            api_key = settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider)
            else:
                if not api_key:
                    return {"models": [], "success": False,
                           "error": "API key required for this provider"}
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key)

            # Check if provider supports embeddings
            if not provider_instance.supports_embeddings():
                return {"models": [], "success": False,
                       "error": f"{provider} does not support embeddings"}

            models = provider_instance.get_available_embedding_models()
            return {"models": models, "success": True}
        except Exception as e:
            logger.error(f"Error fetching embedding models for {provider}: {e}")
            return {"models": [], "success": False, "error": str(e)}

    def set_embedding_config(self, provider, model=None):
        """Set the embedding provider and model."""
        try:
            from settings.llm_provider import ProviderFactory

            # Validate that provider supports embeddings
            settings_manager = SettingsContext.get_settings_manager()
            api_key = settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider)
            else:
                if not api_key:
                    return {"success": False,
                           "error": f"API key required for {provider}. Please set it first."}
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key)

            if not provider_instance.supports_embeddings():
                return {"success": False,
                       "error": f"{provider} does not support embeddings. Choose OpenAI, Google, or Ollama."}

            # Save configuration
            settings_manager.set_embedding_config(provider, model)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting embedding config: {e}")
            return {"success": False, "error": str(e)}

    # ========== Thinking/Reasoning Configuration API Endpoints ==========

    def get_thinking_config(self):
        """Get thinking/reasoning configuration."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            config = settings_manager.get_thinking_config()
            return config
        except Exception as e:
            logger.error(f"Error getting thinking config: {e}")
            return {
                "enabled": False,
                "budget_tokens": 2000,
                "effort": "medium",
                "summary": "auto"
            }

    def set_thinking_config(self, config):
        """Set thinking/reasoning configuration."""
        try:
            settings_manager = SettingsContext.get_settings_manager()
            settings_manager.set_thinking_config(config)
            return {"success": True}
        except Exception as e:
            logger.error(f"Error setting thinking config: {e}")
            return {"success": False, "error": str(e)}

    def check_thinking_support(self, provider, model):
        """Check if a provider/model supports thinking/reasoning."""
        from settings.llm_provider import ProviderFactory
        try:
            settings_manager = SettingsContext.get_settings_manager()
            api_key = settings_manager.get_provider_api_key(provider)

            if provider == 'ollama':
                provider_instance = ProviderFactory.get_provider(provider, model=model)
            else:
                provider_instance = ProviderFactory.get_provider(provider, api_key=api_key, model=model)

            supports_thinking = provider_instance.supports_thinking()
            return {"supports_thinking": supports_thinking, "success": True}
        except Exception as e:
            logger.error(f"Error checking thinking support for {provider}/{model}: {e}")
            return {"supports_thinking": False, "success": False, "error": str(e)}


def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists("../gui/index.html"):  # unfrozen development
        return "../gui/index.html"
    if exists("../Resources/gui/index.html"):  # frozen py2app
        return "../Resources/gui/index.html"
    if exists("./gui/index.html"):
        return "./gui/index.html"
    raise Exception("No index.html found")

entry = get_entrypoint()

def anki_close_dialog(window):
    window.create_confirmation_dialog('NOTICE', f'Please close Anki before restarting FLASH!')
    window.destroy()
    exit(1)

if __name__ == "__main__":
    logging.debug("Starting application")
    api = Api()
    window = webview.create_window("FLASH", entry, maximized=True, js_api=api)

    try:
        logging.debug("Initializing SettingsManager")
        settings_manager = SettingsManager()
        SettingsContext.set_settings_manager(settings_manager)
        logging.debug("SettingsManager initialized successfully")
        window.events.loaded += lambda: check_settings(window)
        logging.debug("Starting webview")
        webview.start()
    except DBError as e:
        logging.error(f"DBError occurred: {str(e)}")
        webview.start(anki_close_dialog, window)
    except Exception as e:
        logging.error(f"Unexpected error occurred: {str(e)}")

    